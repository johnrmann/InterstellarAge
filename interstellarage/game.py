"""
InterstellarAge
"""

# Import python modules
from datetime import datetime

# Import Flask
from flask import Blueprint, request

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy, event

# Import the database from the main file
from interstellarage import db

# Import the user class
import player as player_lib
import galaxy as galaxy_lib
import orders as order_lib

# Define global variables.
GAME_MIN_PLAYERS = 1
GAME_MAX_PLAYERS = 4

MIN_JOINCODE_LENGTH = 1
MAX_JOINCODE_LENGTH = 25

game_pages = Blueprint('game_pages', __name__)


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

    def on_load(self, context):
        pass

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

        # Declare global variables.
        global GAME_MIN_PLAYERS

        # Preconditions
        assert len(self.players) >= GAME_MIN_PLAYERS

        # Setup the galaxy for this game.
        game_galaxy = Galaxy(self, generate=True)
        self.galaxy = game_galaxy

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



@game_pages.route('/game/create')
def web_create_game():
    # Declare global variables
    global MIN_JOINCODE_LENGTH
    global MAX_JOINCODE_LENGTH

    import user as user_lib
    user = user_lib.current_user()

    if user is None:
        return "Not logged in", 400

    # Get the given join code
    join_code = request.form['join_code']
    assert len(join_code) in range(MIN_JOINCODE_LENGTH, MAX_JOINCODE_LENGTH)

    # Ensure that the faction code looks good
    faction_code = int(request.form['faction'])
    # TODO

    # Create the game.
    new_game = Game(join_code)
    new_game.creator_unique = user.unique
    db.session.commit()

    # Create the Player for the User
    new_player = Player(user, game, faction_code)
    return "Game created"



@game_pages.route('/game/join/<gameid>')
def web_join_game(gameid):
    import user as user_lib
    user = user_lib.current_user()
    game = find(unique=gameid)

    if user is None:
        return "Not logged in", 400
    elif game is None:
        return "Game does not exist.", 400

    # Get the given join code
    join_code = request.form['join_code']

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



event.listen(Game, 'load', Game.on_load)
