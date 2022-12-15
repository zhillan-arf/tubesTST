# TUGAS 5 IMPLEMENTASI API
# MODEL

#  External imports
import mysql.connector

# DB model
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="us_accidents"
)
