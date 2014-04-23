"""
InterstellarAge
"""

# Import python modules
from datetime import datetime

# Import Flask
from flask import request

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import the database from the main file
from interstellarage import db

# Import the user class
import galaxy as galaxy_lib
import orders as order_lib

# Define global variables.
GAME_MIN_PLAYERS = 1
GAME_MAX_PLAYERS = 4

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
    join_code = db.Column(db.String)

    def __init__ (self, join_code):
        """
        TODO
        """

        self.started_when = datetime.now()
        self.on_turn = -1
        self.started = False
        self.join_code = join_code

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

    def faction_shortname_for_user(self, user):
        for player in self.players:
            if player.user == user:
                return player.faction_shortname()
        return ""

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
    # Create the game object.
    game = Game(join_code)

    # Create the player object.
    player = Player(user, game, faction)

    # Return the URL of the game
    return "/game/{0}".format(str(game.unique))



def find(unique=None):
    """
    Keyword Args:
        unique (int):

    Returns:
        A `Game` with matching parameters or `None` if no such `Game` was
        found.
    """

    if unique != None:
        return Game.query.filter_by(unique=unique).first()
    else:
        return None



@app.route('/game/create')
def web_create_game():
    import user as user_lib
    user = user_lib.current_user()

    if user is None:
        return "Not logged in", 400

    # TODO
    return



@app.route('/game/join/<gameid>')
def web_join_game(gameid):
    import user as user_lib
    user = user_lib.current_user()
    game = find(unique=gameid)

    if user is None:
        return "Not logged in", 400
    elif game is None:
        return "Game does not exist.", 400

    # Get the given join code
    join_code = request.find['join_code']

    # Is the game full?
    # Did we get the join_code right?
    if join_code is not game.join_code:
        return "Incorrect password", 400
    # Has the game already started?
    if game.started:
        return "Game already started.", 400
    # Is the desired faction alright?

    # Success!
    pass
