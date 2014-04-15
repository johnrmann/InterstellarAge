"""
InterstellarAge
"""

# Import python modules
from datetime import datetime

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import the database from the main file
from interstellarage import db

# Import the user class
from user import User

# Define global variables
FACTION_CODE_ISCA = 0
FACTION_CODE_GALAXYCORP = 1
FACTION_CODE_FSR = 2
FACTION_CODE_PRIVATEER = 3
NUMBER_OF_FACTIONS = 4

class Game(db.Model):
    """
    Attributes:
        unique (int): This `Game`'s unique identifier.
        started_when (datetime): The date and time the game was started.

        user_isca_id (int):
        user_fsr_id (int):
        user_galaxycorp_id (int):
        user_privateer_id (int):
    """

    __tablename__ = 'game'

    unique = db.Column(db.Integer, primary_key=True)
    started_when = db.Column(db.DateTime)

    user_isca_id = db.Column(db.Integer, db.ForeignKey('user.unique'))
    user_fsr_id = db.Column(db.Integer, db.ForeignKey('user.unique'))
    user_galaxycorp_id = db.Column(db.Integer, db.ForeignKey('user.unique'))
    user_privateer_id = db.Column(db.Integer, db.ForeignKey('user.unique'))

    user_isca = db.relationship("User", backref=db.backref('games_as_isca'))
    user_fsr = db.relationship("User", backref=db.backref('games_as_fsr'))
    user_galaxycorp = db.relationship("User", backref=db.backref('games_as_galaxycorp'))
    user_privateer = db.relationship("User", backref=db.backref('games_as_privateer'))

    def __init__ (self, isca=None, fsr=None, galaxycorp=None, privateer=None):
        """
        Keyword Args:
            isca (User):
            fsr (User):
            galaxycorp (User):
            privateer (User):
        """

        if isca is not None:
            self.user_isca = isca
            self.user_isca_id = isca.unique
        elif fsr is not None:
            self.user_fsr = fsr
            self.user_fsr_id = fsr.unique
        elif galaxycorp is not None:
            self.user_galaxycorp = galaxycorp
            self.user_galaxycorp_id = galaxycorp.unique
        elif privateer is not None:
            self.user_privateer = privateer
            self.user_privateer_id = privateer.unique
        else:
            # TODO error
            pass

        self.started_when = datetime.now()

        # Save changes to the sql database
        db.session.add(self)
        db.session.commit()

    def has_user(self, user):
        cond1 = user == self.user_isca
        cond2 = user == self.user_fsr
        cond3 = user == self.user_galaxycorp
        cond4 = user == self.user_privateer

        return cond1 or cond2 or cond3 or cond4

    def open_slots(self):
        slots = []
        if self.user_isca is None:
            slots.append("ISCA")
        if self.user_fsr is None:
            slots.append("FSR")
        if self.user_galaxycorp is None:
            slots.append("GalaxyCorp")
        if self.user_privateer is None:
            slots.append("Privateer")
        return slots



def create_game(user, faction):
    pass
