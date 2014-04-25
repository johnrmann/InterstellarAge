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
    Objects of the `Player` class serve as a container of sorts for objects
    of the `User` class.

    Since users can play different games at the same time, it does not make
    sense to store game information like money and factions inside the user
    table. This is why we use the `Player` class to store information such as
    the faction a user is playing as in a certain game and the amount of money
    a user has in a certain came.

    Attributes:
        unique (int): Uniquely identifies this player. Assigned by the SQL
            database.

        user_id (int): The `unique` attribute of the `User` this `Player`
            represents.

        game_id (int): The `unique` attribute of the `Game` this `Player` is
            playing.

        user (User): The actual `User` this `Player` represents.

        game (Game): The actual `Game` this `Player` is playing.

        faction_code (int): The code for the faction that the user is playing
            as in this game.

        money (int): The amount of money (in interstellar dollars) that this
            player has available to spend.
    """

    __tablename__ = 'player'
    __table_args__ = {'extend_existing':True}

    unique = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.unique'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.unique'))

    user = db.relationship('User', backref='playing')
    game = db.relationship('Game', backref='players')

    faction_code = db.Column(db.Integer)
    money = db.Column(db.Integer)

    def __init__(self, user, game, faction_code):
        """
        This is the constructor for the `Player` class.

        Args:
            user (User): The `User` this `Player` represents.

            game (Game): The `Game` that this `Player` will be part of.

            faction_code (int): The `int` identifying the faction that the
                user wishes to play as.
        """

        # Preconditions.
        assert user is not None
        assert game is not None
        assert check_faction(faction_code)

        # Assign attributes.
        self.user_id = user.unique
        self.game_id = game.unique
        self.user = user
        self.game = game
        self.faction_code = faction_code
        self.money = -1

        # Record this new player in the SQL database.
        db.session.add(self)
        db.session.commit()

    def faction_shortname(self):
        """
        Returns a `str` representing the short name for the faction that this
        Player is playing.
        """

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
        """
        Returns a `str` representing the full "fancy" name for the faction that
        this Player is playing.
        """

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



def check_faction(faction_code):
    """
    This function checks to see if a given `int` is a faction code defined in
    the beginning of this module.

    Args:
        faction_code (int): The faction code we wish to check.

    Returns:
        `True` if and only if the given `faction_code` is one defined as a
        constant in this module.
    """

    global FACTION_CODE_ISCA
    global FACTION_CODE_GALAXYCORP
    global FACTION_CODE_FSR
    global FACTION_CODE_PRIVATEER

    codes = [
        FACTION_CODE_ISCA,
        FACTION_CODE_GALAXYCORP,
        FACTION_CODE_FSR,
        FACTION_CODE_PRIVATEER
    ]

    return faction_code in codes
