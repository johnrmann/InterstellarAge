"""
InterstellarAge
"""

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy.orm import relationship

# Import the database from the main file
from interstellarage import db

# Import the game class
from game import Game

# Define global variables
USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 32

class User(db.Model):
    """
    TODO

    Public Attributes:
        unique (int):
        username (str): TODO
        password_hash (str): The hashed version of this `User`'s password.
        email (str): The `User`'s e-mail address.
    """

    __tablename__ = 'user'

    unique = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)

    games_as_isca = relationship("Game")
    games_as_galaxycorp = relationship("Game")
    games_as_fsr = relationship("Game")
    games_as_privateer = relationship("Game")

    def __init__(self, username, password_hash, email):
        """
        Validates and assigns data.

        Precondition:
            The password before becomming `password_hash` was checked for
            length.
        """

        global USERNAME_MIN_LENGTH
        global USERNAME_MAX_LENGTH

        # Validate username input -- check length and ensure that nobody else
        # has chosen this username.
        assert USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH

        # Validate email input -- check length and ensure that it matches the
        # regular expression for an email address
        # TODO

        # Assign data
        self.username = username
        self.password_hash = password_hash
        self.email = email

        # Record this new user in the SQL database
        db.session.add(self)
        db.session.commit()

    def get_games(self):
        """
        Returns a list of all the `Game`s this `User` is part of.
        """

        return []



def find(unique=None, username=None, email=None):
    """
    Finds a user and returns their `User` object.

    Args:
        unique (int): The `User`'s unique ID given to it during the initial SQL
            insert query.
        username (str):
        email (str):

    Returns:
        The `User` object if it was found. If it wasn't found, then `None` is
        returned.
    """

    if unique == None and username == None and email == None:
        return None

    # Find with unique
    elif unique != None:
        return User.query.filter_by(unique=unique).first()

    # Find with username
    elif username != None:
        return User.query.filter_by(username=username).first()

    # Find with email
    elif email != None:
        return User.query.filter_by(email=email).first()
