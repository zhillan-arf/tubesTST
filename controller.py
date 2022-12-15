# TUGAS 5 IMPLEMENTASI API
# 18220008 Zhillan Attarizal Rezyarifin
# CONTROLLER - PROGRAM UTAMA

# External imports
from flask import Flask, request, redirect, url_for, jsonify, Response, send_file
from pandas.io.json import json_normalize
from urllib.parse import quote, unquote
from functools import wraps
import matplotlib.pyplot as plt
import pandas as pd
import requests
import jwt
import json

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


# (2/3) CORE 
# PROVIDE | Parse received JSON, join
@app.route("/getmap", methods=["GET", "POST"])
@needs_token
def getmap():
    # Load JSON file
    request.get_json()
    dict_accs = json.loads(request.data, strict=False)
    df_accs = pd.DataFrame(dict_accs["accidents"])

    # Load MySQL file
    cursor = mydb.cursor()
    script = "SELECT NAME, STUSAB, INTPTLAT, INTPTLON FROM us_counties_borders"
    cursor.execute(script)
    df_coor= pd.DataFrame(cursor.fetchall(), columns=["NAME", "STUSAB", "INTPTLAT", "INTPTLON"])

    df_coor["INTPTLAT"] = df_coor["INTPTLAT"].astype(float)
    df_coor["INTPTLON"] = df_coor["INTPTLON"].astype(float)

    df_joined = pd.merge(df_accs, df_coor, on=["NAME", "STUSAB"])
    
    # Convert back to JSON
    d_joined = df_joined.to_json(orient="records")

    return jsonify({"accidents" : d_joined}), 200

# RECEIVE | Visualize statistics on image
@app.route("/vizstats", methods=["GET", "POST"])
@needs_token
def vizstats():
    # Login to zhaf's server w/ hard-coded creds
    path_zhaf = "http://103.13.207.181:5000"
    endpoint = "/loginapi/"
    email = "muhammad.zhafran.haris@gmail.com"
    password = "2345"
    url_request_token = path_zhaf + endpoint + "?email=" + email + "&password=" + password
    rtoken = requests.post(url_request_token)
    json_rtoken = rtoken.json()
    token = json_rtoken["Token"]
    
    # Get statistic from zhaf's server
    startdate = request.args.get("startdate")
    enddate = request.args.get("enddate")
    endpoint = "/report"
    url_request_stats = path_zhaf + endpoint + "?token=" + token + "&startdate=" + startdate + "&enddate=" + enddate
    rstats = requests.get(url_request_stats)
    rjson = rstats.json()

    # Get statistics
    df_daily = pd.DataFrame(columns=["date", "total accidents", "avg severity", "weight"])
    for item in rjson:
        df_daily = df_daily.append(
            {
                "date" : item,
                "total accidents" : rjson[item]["total accidents"], 
                "avg severity" : rjson[item]["avg severity"],
                "weight" : rjson[item]["total accidents"] * rjson[item]["avg severity"]
            }, 
            ignore_index=True
        )
    df_daily.plot()
    plt.savefig("stats.png")
    
    return send_file("stats.png", mimetype="image/png")

# (3/3) ROOT
@app.route("/")
@needs_token
def index():
    token = request.args.get("token")
    return jsonify(f"Hello, world!\nToken (testing purposes): {token}\nPlease save this temporary token for use."), 200

# RUN
if __name__ == "__main__":
    app.run()
