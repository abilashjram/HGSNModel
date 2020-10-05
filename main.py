import random
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db
import uuid
import hashlib

app = Flask(__name__)

#create database
db.create_all()



@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    #hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    #create the secret number
    secret_number =  random.randint(1,30)

    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)

        # save it into db
        db.add(user)
        db.commit()

    #check if the passwords match
    if hashed_password != user.password:
        return "Wrong Password!"
    elif hashed_password == user.password:
        #create a random session token
        session_token = str(uuid.uuid4())

        user.session_token = session_token

        # save it into db
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response

    #
    # response = make_response(redirect(url_for("index")))
    # response.set_cookie("email", email)
    #
    # return response

@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()


    if guess == user.secret_number :
        message = "Congrats! The secret number is {0}".format(str(user.secret_number))

        new_secret = random.randint(1,30)
        user.secret_number = new_secret
        # save it into db
        db.add(user)
        db.commit()

    elif guess > user.secret_number:
        message = "Wrong! Try something smaller"
    else:
        message = "Wrong! Try something bigger"

    return render_template("result.html", message=message)

if __name__ == '__main__':
    app.run()