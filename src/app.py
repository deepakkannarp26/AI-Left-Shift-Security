from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):
        return "Logged in"

    return "Invalid"


if __name__ == "__main__":
    app.run(debug=True)









