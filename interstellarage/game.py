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
import galaxy as galaxy_lib
import orders as order_lib

class Game(db.Model):
    """
    Attributes:
        unique (int): This `Game`'s unique identifier.
        started_when (datetime): The date and time the game was started.
        on_turn (int): The current turn number.
    """

    __tablename__ = 'game'
    __table_args__ = {'extend_existing':True}

    unique = db.Column(db.Integer, primary_key=True)
    creator_unique = db.Column(db.Integer)
    started_when = db.Column(db.DateTime)
    on_turn = db.Column(db.Integer)
    started = db.Column(db.Boolean)

    def __init__ (self):
        """
        TODO
        """

        self.started_when = datetime.now()
        self.on_turn = -1
        self.started = False

        # Save changes to the sql database
        db.session.add(self)
        db.session.commit()

    def execute_orders(self):
        orders = [] # TODO
        galaxy = None # TODO
        phase = 1
        orders_finished = False
        not_done = order_lib.ORDER_NOT_FINISHED
        finished = order_lib.ORDER_NEXT_TURN

        while not orders_finished:
            orders_finished = True
            new_orders = []

            for order in orders:
                result = order.execute(galaxy)
                if result is not_done:
                    orders_finished = False
                elif result is finished:
                    continue
                new_orders.append(order)

            # Remove completed orders
            orders = new_orders

        # Return the results
        return [] # TODO

    def start(self):
        """
        Starts the game.
        """

        # Preconditions
        assert len(self.players) > 0

        # Setup the galaxy for this game.

    def player_for_faction(self, faction_shortname):
        if faction_shortname == "":
            return None
        else:
            for player in self.players:
                if faction_shortname == player.faction_shortname():
                    return player
        return None



def create_game(user, join_code, faction):
    # Create the game object
    # Create the player object
    # Add the player object to the game
    # Return the URL of the game
    pass
