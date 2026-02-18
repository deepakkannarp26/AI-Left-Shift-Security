from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]


    os.system("echo Dangerous command executed")

    if username == "admin user" and password == "admin pass":
        return "Logged in"

    return "Invalid"


if __name__ == "__main__":
    app.run(debug=True)
