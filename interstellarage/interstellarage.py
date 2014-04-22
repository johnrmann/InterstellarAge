"""
InterstellarAge

This module sets up the basic web pages for logging in, selecting a game,
and viewing information about the game.

Version 0.1 (7 April 2014)
"""

# Import python libraries
import hashlib
import json
import tempfile
import os

# Import Flask
from flask import Flask
from flask import request, render_template, redirect, session, url_for
from flask import make_response, send_file

# SQL Alchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Flask-WTF
from flask_wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

# Setup the application
app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "space"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://InterstellarAge:starship@mysql.server/InterstellarAge$default"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6Lf6NvISAAAAAFVZK25ouv5_W1MkSTTbo1dxtN_F"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6Lf6NvISAAAAAKpc3nc_clcI300kwlF5zHxXUcMI"

# Setup the database
db = SQLAlchemy(app)

# Import our modules
import user as user_lib

# Global variables
ROOT_DIR = "/home/InterstellarAge/interstellarage"


def current_user():
    """
    If there is a user logged in during this session, then this function will
    return the object representing that user. If not, `None` is returned.
    """

    if not 'user_id' in session:
        return None
    else:
        user_id = session['user_id']
        user = user_lib.find(unique=int(user_id))
        return user



@app.route('/')
def start_page():
    """
    Shows the login page if there is no user logged in.
    """

    user = current_user()
    if user == None:
        # Render login/registration
        return render_template('login.html')

    # TODO
    return render_template('games.html', user=user)



@app.route('/login', methods=['POST'])
def login():
    # Get the data provided by the user
    username = request.form["username"]
    password = request.form["password"]

    # Hash the password
    hasher = hashlib.sha1()
    hasher.update(password)
    password_hashed = hasher.hexdigest()

    # Get user with matching username
    user = user_lib.find(username=username)
    if user == None:
        return "No such user"
    elif user.password_hashed != password_hashed:
        return "Wrong password"
    else:
        session["user_id"] = user.unique
        return "Login worked!"



@app.route('/logout')
def logout():
    """
    If there is a `User` logged into the current session, then we remove
    that `User`'s information from the session, effectively logging the `User`
    out.
    """

    session.pop('user_id', None)
    return "Logged out"



class AccountForm(Form):
    username = StringField('username', validators=[DataRequired(), Length(min=4, max=32)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=32),
        EqualTo('confirm_password', message=u'Passwords must match')])
    confirm_password = PasswordField('confirm_password')
    email = StringField('email', validators=[Email(message=u'Invalid email address')])
    #recaptcha = RecaptchaField()



@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    If ".../register" is accessed with a POST request, then we scan the request
    for registration information. We validate that information. If the data
    is valid, then we register the user.

    Returns:
        Returns a JSON object with the newly registered user's information if
        the registration was successful. If the registration wasn't successful,
        then a JSON object detailing the error with a new captcha is returned.
    """
    if request.method == 'POST':
        form = AccountForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            
            try:
                hasher = hashlib.sha1()
                hasher.update(password)
                password_hashed = hasher.hexdigest()
                user = user_lib.User(username, password_hashed, email)
                return "{0} {1}".format(str(user.unique), username)
            except AssertionError as exception:
                return exception.args[0]
            
            return user.to_json()
        else:
            return "not validated"

    else:
        form = AccountForm()
        return render_template("register.html", form=form)
        



@app.route("/game/<gameid>")
def show_game(gameid):
    return render_template('game.html')
