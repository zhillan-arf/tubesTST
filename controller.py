# TUGAS 5 IMPLEMENTASI API
# 18220008 Zhillan Attarizal Rezyarifin
# CONTROLLER - PROGRAM UTAMA

# External imports
from flask import Flask, request, redirect, url_for, jsonify, Response, send_file
from pandas.io.json import json_normalize
from urllib.parse import quote, unquote
from functools import wraps
import pandas as pd
import requests
import jwt

# CONTROLLLER
app = Flask(__name__)
SECRET_KEY = "miio1206"

# MODEL
from tools.hashing import hash_three, verified, generate_salt
from models import mydb

# VIEW (ROUTES)
# (1/3) AUTHENTICATION

# Token-checking wrapper function
def needs_token(func):
    @wraps(func)
    def wrap_token_checker(*args, **kwargs):
        token = request.args.get('token')
        username = request.args.get('username')
        if not token or not username:
            # func is not processed
            return jsonify("Please login before accessing this page."), 401
        # Token detected
        try:
            token_test = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.DecodeError:
            # func is not processed
            return jsonify("Your access permission is invalid."), 401
        # func is processed!
        return func(*args, **kwargs)
    return wrap_token_checker

# Login and grant token 
@app.route("/login", methods=["GET", "POST"])
def login():
    # Get data
    cursor1 = mydb.cursor()
    username = request.args.get('username')
    password = request.args.get('password')
    if username is None or password is None:
        return jsonify("Please provide a valid username and password."), 403
    script_get = "SELECT * FROM users WHERE username =%s"
    cursor1.execute(script_get, (username,))
    user_row = cursor1.fetchone()
    # Authenticate username and password, token
    if user_row is None:
        # Fail!
        return jsonify("Your account does not exist."), 403
    hashpass = user_row[1]
    salt = user_row[2]
    if verified(username, password, salt, hashpass):
        # Success! Grant token
        token = jwt.encode({"username" : username}, SECRET_KEY, algorithm="HS256")
        return redirect(url_for('index')+"?username="+username+"&token="+token)
    # Fail!
    return jsonify("You're not authorized to use this feature."), 401

# Sign up user using URL query
@app.route("/signup", methods=["GET", "POST", "PUT"])
def signup():
    cursor2 = mydb.cursor()
    username = request.args.get('username')
    password = request.args.get('password')
    # Check existence of parameters
    if not username or not password:
        return jsonify("Please enter a username and a password!"), 400
    
    # Check is username already exists
    script = "SELECT username FROM users WHERE username=%s"
    cursor2.execute(script, (username,))
    old_user = cursor2.fetchone()
    if old_user is not None:
        return jsonify("This username already exists!"), 400
    mydb.commit()
    # Signup new user
    salt = str(generate_salt())
    hashed = hash_three(username, password, salt)
    script_input = "INSERT INTO users(username, hashpass, salt) VALUES (%s, %s, %s)"
    cursor2.execute(script_input, (username, hashed, salt))
    mydb.commit()
    return jsonify("You have successfully signed up."), 200


# (2/3) CORE API
# PROVIDE | Parse received JSON, join
@app.route("/getmap", methods=["GET", "POST"])
@needs_token
def getmap():
    # Get list data from JSON file
    d_json = request.get_json()
    
    # Convert djson["accidents"] into a pd.DataFrame
    df_accs = json_normalize(d_json, "accidents")

    # Get counties coordinates data (dcoor)
    cursor = mydb.cursor()
    script = "SELECT NAME, STUSAB, INTPTLAT, INTPTLON FROM us_counties"
    cursor.execute(script)
    df_coor= pd.DataFrame(cursor.fetchall())

    # Join the dataframes
    df_joined = pd.merge(df_accs, df_coor, on=["NAME", "STUSAB"])

    # Covert to JSON
    d_joined = df_joined.to_json(orient="records")

    # return jsonify(d_joined), 200
    return "test", 200

# RECEIVE | Visualize statistics on image
@app.route("/vizstats", methods=["GET", "POST"])
@needs_token
def vizstats():
    # Login to zhaf's server w/ hard-coded creds
    path_zhaf = ""
    endpoint = "/loginapi"
    email = "muhammad.zhafran.haris@gmail.com"
    password = "2345"
    url_request_token = path_zhaf + endpoint + "?email=" + email + "&password=" + password
    rtoken = requests.get(url_request_token)
    token = (rtoken.json())["token"]
    
    # Get statistic from zhaf's server
    startdate = request.args.get("startdate")
    enddate = request.args.get("enddate")
    endpoint = "/report"
    url_request_stats = path_zhaf + endpoint + "?token=" + token + "&startdate=" + startdate + "&enddate=" + enddate
    rstats = requests.get(url_request_stats)
    rdata = rstats.json()
    stats = rdata["statistic"]

    # Get daily statistics
    df_daily = pd.DataFrame(columns=["date", "total accidents", "avg severity", "weight"])
    for key, value in stats.items():
        df_daily = df_daily.append(
            {
                "date" : key, 
                "total accidents" : value["total accidents"], 
                "avg severity" : value["avg severity"],
                "weight" : value["total accidents"] * value["avg severity"]
            }, 
            ignore_index=True
        )
    fig_daily = df_daily.figure()
    fig_daily.savefig("stats.png")
    
    return send_file("stats.png", mimetype="image/png")

# (3/3) ROOT
@app.route("/")
@needs_token
def index():
    token = request.args.get("token")
    return f"Hello, world!\nToken (testing purposes): {token}\nPlease save this temporary token for use.", 200

# RUN
if __name__ == "__main__":
    app.run()
