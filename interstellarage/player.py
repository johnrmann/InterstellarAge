"""
InterstellarAge
"""

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import the database from the main file
from interstellarage import db

# Import our modules
import game as game_lib
import user as user_lib

# Define global variables
PLAYER_START_MONEY = 1000
FACTION_CODE_ISCA = 0
FACTION_CODE_GALAXYCORP = 1
FACTION_CODE_FSR = 2
FACTION_CODE_PRIVATEER = 3
NUMBER_OF_FACTIONS = 4

class Player(db.Model):
    """
    TODO

    Attributes:
    """

    __tablename__ = 'player'
    __table_args__ = {'extend_existing':True}

    user_id = db.Column(db.Integer, db.ForeignKey(user_lib.User.unique))
    game_id = db.Column(db.Integer, db.ForeignKey(game_lib.Game.unique))

    user = db.relationship(user_lib.User, backref='playing')
    game = db.relationship(game_lib.Game, backref='players')

    faction_code = db.Column(db.Integer)
    money = db.Column(db.Integer)

    def __init__ (self, user, game, faction_code):
        """
        TODO
        """

        self.user_id = user.unique
        self.game_id = game.unique
        self.faction_code = faction_code

        # Record this new player in the SQL database
        db.session.add(self)
        db.session.commit()

    def faction_shortname(self):
        global FACTION_CODE_ISCA
        global FACTION_CODE_GALAXYCORP
        global FACTION_CODE_FSR
        global FACTION_CODE_PRIVATEER

        if self.faction_code == FACTION_CODE_ISCA:
            return "ISCA"
        elif self.faction_code == FACTION_CODE_GALAXYCORP:
            return "GalaxyCorp"
        elif self.faction_code == FACTION_CODE_PRIVATEER:
            return "Mercs"
        elif self.faction_code == FACTION_CODE_FSR:
            return "FSR"
        else:
            return None

    def faction_name(self):
        global FACTION_CODE_ISCA
        global FACTION_CODE_GALAXYCORP
        global FACTION_CODE_FSR
        global FACTION_CODE_PRIVATEER

        if self.faction_code == FACTION_CODE_ISCA:
            return "International Space Commerce Administration"
        elif self.faction_code == FACTION_CODE_GALAXYCORP:
            return "Galactic Resources Corporation"
        elif self.faction_code == FACTION_CODE_PRIVATEER:
            return "Mercenary Alliance"
        elif self.faction_code == FACTION_CODE_FSR:
            return "Foundation for Scientific Research"
        else:
            return None

    def start(self):
        """
        Sets up this `Player` for the start of the game.
        """

        global PLAYER_START_MONEY
        self.money = PLAYER_START_MONEY
        db.session.commit()
