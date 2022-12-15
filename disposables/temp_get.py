from flask import Flask, request, jsonify
from matplotlib import pyplot as plt
import mysql.connector

app = Flask(__name__)

# Connect to the local MySQL database and get the place_coordinates table
mydb = mysql.connector.connect(
  host="localhost",
  user="<username>",
  password="<password>",
  database="<database_name>"
)
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM place_coordinates")
place_coordinates = mycursor.fetchall()

@app.route('/plot', methods=['POST'])
def plot():
    # Get the data from the JSON file
    data = request.get_json()

    # Initialize empty lists for the x and y coordinates
    xs = []
    ys = []
    sizes = []

    # Loop through the data and get the x and y coordinates from the place_coordinates table
    for entry in data:
        place_name = entry["place_name"]
        size = entry["size"]

        # Loop through the place_coordinates table and find the entry with the same place name
        for coord in place_coordinates:
            if coord[0] == place_name:
                xs.append(coord[1])
                ys.append(coord[2])
                sizes.append(size)

    # Create a scatter plot using matplotlib
    plt.scatter(xs, ys, sizes)

    # Save the figure as a PNG file
    plt.savefig('plot.png')

    # Return the PNG file to the requester
    with open('plot.png', 'rb') as f:
        return f.read()

if __name__ == '__main__':
    app.run()