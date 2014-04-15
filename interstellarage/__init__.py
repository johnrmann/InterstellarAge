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

# Setup the application
app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "space"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://InterstellarAge:starship@localhost/$default"

# Setup the database
db = SQLAlchemy(app)

# Global variables
ROOT_DIR = "/home/InterstellarAge/interstellarage"

def assign_captcha():
    """
    Randomly creates a captcha (used to determine if a user is a human or
    a computer), assigns it to the session, and returns it as a string.

    Returns:
        The generated captcha as an `str`.
    """

    captcha_words = ["galaxy", "nebula", "earth", "mars", "saturn", "neptune",
                     "jupiter", "venus", "sirius", "rigel", "vega", "mercury",
                     "andromeda", "nova", "quasar", "spacetime", "star"]

    # Pick a random word from the list and pick a random integer
    import random
    random_word = random.choice(captcha_words)
    random_int = random.randint(0,1000)

    # Create the captcha string and assign it to the session
    captcha = "{0} {1}".format(random_word, str(random_int))
    session['captcha'] = captcha
    return captcha



def captcha_image(captcha):
    """
    Args:
        captcha (str): The Captcha to display.

    Returns:
        An `str` containing binary PNG data. This image depicts `captcha` as
        an image.
    """

    # Declare global variables
    global ROOT_DIR

    # Import Image from the Python Image Library
    from PIL import Image, ImageDraw, ImageFont

    # Create the blank image
    im = Image.new("RGB", (100, 40), "white")
    draw = ImageDraw.Draw(im)

    # Get the font and draw the provided text.
    font_path = ROOT_DIR+"/static/ttf/font.ttf"
    font = ImageFont.truetype(font_path, 30, encoding="unic")
    draw.text((5,5), captcha, font=font, fill="black")
    del draw

    # Save the image data
    im_path = ROOT_DIR+"/temporary/captcha.png"
    im.save(file(im_path, 'wb'), "PNG")
    del im
    im_file = open(im_path)

    # Copy the image to a temporary file.
    from shutil import copyfileobj
    temp_im_file = tempfile.NamedTemporaryFile(mode='w+b',suffix='png')
    copyfileobj(im_file, temp_im_file)
    im_file.close()
    os.remove(im_path)

    # Return the temporary image.
    return temp_im_file



def current_user():
    """
    If there is a user logged in during this session, then this function will
    return the object representing that user. If not, `None` is returned.
    """

    if not 'user_id' in session:
        return None
    else:
        user_id = session['user_id']
        # TODO get the user
        import user as user_lib
        user = user_lib.find(unique=int(user_id))
        return user



@app.route('/')
def start_page():
    """
    Shows the login/register page if there is no user logged in.
    """

    user = current_user()
    if user == None:
        # Render login/registration
        return render_template('login.html')

    # TODO
    return 'Hello from Flask!'



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
    import user as user_lib
    user = user_lib.find(username=username)
    if user == None:
        return "Login failed"
    elif user.password_hashed != password_hashed:
        return "Wrong password"
    else:
        session["user_id"] = user.unique
        return "Login worked!"



@app.route('/register', methods=['POST'])
def register():
    """
    If ".../register" is accessed with a POST request, then we scan the request
    for registration information. We validate that information. If the data
    is valid, then we register the user.

    Request Fields (POST):
        username (str): The user's desired username.
        password (str): The user's desired password.
        confirm_password (str): For checking password typos.
        email (str): The user's email address.
        captcha (str): To ensure that the user is not a robot.

    Returns:
        Returns a JSON object with the newly registered user's information if
        the registration was successful. If the registration wasn't successful,
        then a JSON object detailing the error with a new captcha is returned.
    """

    # Get data from the form
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    email = request.form["email"]
    provided_captcha = request.form["captcha"]

    # Check password invariants
    if password != confirm_password:
        return registration_error("Passwords do not match")
    elif len(password) < 8:
        return registration_error("Password too short")
    elif len(password) > 32:
        return registration_error("Password too long")

    # Check captcha
    if not 'captcha' in session:
        return "Data not submitted from form"
    real_captcha = session['captcha']
    if real_captcha != provided_captcha:
        assign_captcha()
        return registration_error("Captcha doesn't match. Try again.")

    try:
        user = user.User(username, password_hashed, email)
        return "{0} {1}".format(str(user.unique), username)
    except AssertionError as exception:
        return exception.args[0]

    return user.to_json()



@app.route("/captcha", methods=["POST"])
def get_captcha():
    """
    Creates a new captcha, assigns it to the session, and returns an image
    showing it.

    Returns:
        A `str` containing the raw binary data of a PNG image.
    """

    image = captcha_image(assign_captcha())
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/png'
    resp.headers['Content-Disposition'] = 'attachment; filename=captcha.png'
    return resp



def registration_error(reason):
    """
    Args:
        reason (str): The reason why the registration wasn't successful.

    Returns:
        A 400 error with text containing a JSON object containing a reason for
        the failure and a new captcha image.
    """

    new_captcha = assign_captcha()

    return json.dumps({
        "reason" : reason,
        "captcha" : captcha_image(new_captcha)
    }), 400
