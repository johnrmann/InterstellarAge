"""
InterstellarAge
game.py
"""

# Import python modules
from datetime import datetime

# Import Flask
from flask import Blueprint, request

# Import SQLAlchemy
from sqlalchemy import event

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
MAX_JOINCODE_LENGTH = 40

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
    join_code = db.Column(db.String(40))

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

    def __contains__(self, other):
        import user as user_lib
        if isinstance(other, player_lib.Player):
            return other in self.players
        elif isinstance(other, user_lib.User):
            return self.player_for_user(other) is not None
        else:
            return False

    def add_user(self, user, faction_code, creator=False):
        """
        Args:
            user (User):
            faction_code (int):

        Keyword Args:
            creator (boolean): Set to `True` if the given `User` created this
                `Game`.

        Returns:
            TODO
        """

        # Preconditions.
        assert not self.full()
        assert not self.faction_taken(faction_code)

        new_player = player_lib.Player(user, self, faction_code)
        if creator:
            self.creator_unique = user.unique
        db.session.commit()
        return new_player

    def on_load(self, context):
        """
        Called after a `Game` object has been loaded from the SQL database.

        This method loads the `Game`'s `Galaxy` and any queued `Order`s from
        the JSON files.
        """

        # If we have not started this game, then we do not need to parse the
        # galaxy or orders.
        if not self.started:
            return

        # Find out where the "data" directory is.
        import os
        current_directory = os.path.dirname(__file__)
        data_directory = current_directory+"/data/"

        # Filenames to open.
        galaxy_filename = "{0}.galaxy.json".format(str(self.unique))
        orders_filename = "{0}.orders.json".format(str(self.unique))
        galaxy_filename = data_directory + galaxy_filename
        orders_filename = data_directory + orders_filename

        # Parse the Galaxy.
        galaxy_file = open(galaxy_filename)
        galaxy_dict = json.reads(galaxy_file.read())
        galaxy_file.close()
        self.galaxy = galaxy_lib.galaxy_from_dict()

        # Parse the orders.
        orders_file = open(orders_filename)
        orders_dict = json.reads(orders_file.read())
        orders_file.close()
        for order in orders_dict['move']:
            parser = order_lib.move_order_from_dict
            as_dict = parser(order, self)
            self.orders.append(as_dict)
        for order in orders_dict['hyperspace']:
            parser = order_lib.hyperspace_order_from_dict
            as_dict = parser(order, self)
            self.orders.append(as_dict)
        for order in orders_dict['build']:
            parser = order_lib.build_fleet_order_from_dict
            as_dict = parser(order, self)
            self.orders.append(as_dict)
        for order in orders_dict['colonize']:
            parser = order_lib.upgrade_planet_order_from_dict
            as_dict = parser(order, self)
            self.orders.append(as_dict)

    def queue_orders(self, orders):
        """
        TODO
        """

        # Add the orders
        self.orders.extend(orders)
        self.commit()

        # See if every player has sent orders. If this is the case, then
        # execute the orders.
        for player in self.players:
            for order in self.orders:
                if order.orderer == player:
                    break
            else:
                return # don't execute

        # Execute the orders
        self.execute_orders()

    def execute_orders(self):
        orders_finished = False
        not_done = order_lib.ORDER_NOT_FINISHED
        finished = order_lib.ORDER_NEXT_TURN

        while not orders_finished:
            orders_finished = True
            new_orders = []

            for order in self.orders:
                result = order.execute(self.galaxy)
                if result == not_done:
                    orders_finished = False
                elif result == finished:
                    continue
                new_orders.append(order)

            # Remove completed orders
            self.orders = new_orders

        # Return the results
        return [] # TODO

    def faction_shortname_for_user(self, user):
        for player in self.players:
            if player.user == user:
                return player.faction_shortname()
        return ""

    def faction_taken(self, faction_code):
        for player in self.players:
            if player.faction_code == faction_code:
                return True
        return False

    def full(self):
        global GAME_MAX_PLAYERS
        return len(self.players) == GAME_MAX_PLAYERS

    def next_turn(self):
        # Add planet GDP to players.
        systems = self.galaxy.systems
        for system in systems:
            planets = system.flat_planets()
            for planet in planets:
                if planet.owner is None:
                    continue
                money = planet.economic_output()
                planet.owner.money += money

        # Increment turn
        self.on_turn += 1
        db.session.commit()

    def start(self):
        """
        Starts the game.
        """

        # Declare global variables.
        global GAME_MIN_PLAYERS

        # Preconditions
        assert len(self.players) >= GAME_MIN_PLAYERS

        # Setup the galaxy for this game.
        game_galaxy = galaxy_lib.Galaxy(self, generate=True)
        self.galaxy = game_galaxy
        self.orders = []
        self.on_turn = 1
        self.started = True
        for player in self.players:
            player.start()
        self.commit()
        db.session.commit()

    def player_for_faction(self, faction_shortname):
        if faction_shortname == "":
            return None
        else:
            for player in self.players:
                if faction_shortname == player.faction_shortname():
                    return player
        return None

    def player_for_user(self, user):
        for player in self.players:
            if player.user == user:
                return player
        print self.players
        print user
        return None

    def player_for_unique(self, unique):
        for player in self.players:
            if player.unique == unique:
                return player
        return None

    def commit(self):
        # Find out where we will write the galaxy and orders.
        import os
        current_directory = os.path.dirname(__file__)
        data_directory = current_directory+"/data/"

        # Get the dict version of the galaxy and write it.
        output = self.galaxy.as_list(discoveries=True)
        galaxy_filename = self.galaxy.get_json_filename()
        galaxy_file = open(data_directory+galaxy_filename, 'w+')
        galaxy_file.write(json.dumps(output))
        galaxy_file.close()

        # Get the dict version of the orders and write it.
        output = {
            'move' : [],
            'hyperspace' : [],
            'build' : [],
            'colonize' : []
        }
        for order in self.orders:
            if not isinstance(order, order_lib.Order):
                raise Exception("Something went wrong - nonorder item in list")
            to_put = order.as_dict()
            output[order.dict_index()].append(to_put)

        # Write it to the file.
        order_filename = "{0}.orders.json".format(str(self.unique))
        order_file = open(data_directory+order_filename, 'w+')
        order_file.write(json.dumps(output))
        order_file.close()



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



@game_pages.route('/game/create', methods=['POST'])
def web_create_game():
    # Declare global variables
    global MIN_JOINCODE_LENGTH
    global MAX_JOINCODE_LENGTH

    from interstellarage import current_user
    user = current_user()

    if user is None:
        return "Not logged in", 400

    # Get the given join code
    join_code = request.form['join_code']
    assert len(join_code) in range(MIN_JOINCODE_LENGTH, MAX_JOINCODE_LENGTH)

    # Ensure that the faction code looks good
    faction_code = int(request.form['faction'])
    # TODO

    # Create the game and add the player who made it.
    new_game = Game(join_code)
    new_game.add_user(user, faction_code, creator=True)

    # Return the URL
    return "/game/{0}".format(str(new_game.unique))



@game_pages.route('/game/join/<gameid>', methods=['POST'])
def web_join_game(gameid):
    from interstellarage import current_user
    user = current_user()
    game = find(unique=int(gameid))

    if user is None:
        return "Not logged in", 400
    elif game is None:
        return "Game does not exist.", 400
    elif game.started:
        return "Game already started.", 400
    elif game.full():
        return "Game full", 400

    # Check to see if the join code is correct.
    join_code = request.form['join_code']
    if join_code != game.join_code:
        return "Incorrect password", 400

    # Is the desired faction alright?
    faction_code = int(request.form['faction'])
    if not player_lib.check_faction(faction_code):
        return "Invalid faction", 400
    elif game.faction_taken(faction_code):
        return "Faction taken", 400

    # Success!
    game.add_user(user, faction_code)
    return "Joined", 200



@game_pages.route('/game/start/<gameid>', methods=['POST'])
def web_start_game(gameid):
    from interstellarage import current_user
    user = current_user()
    game = find(unique=int(gameid))

    if user is None:
        return "Not logged in", 400
    elif game is None:
        return "Game does not exist.", 400
    elif user.unique != game.creator_unique:
        return "Not authorized", 400

    game.start()
    return "Started game"



# When we load a Game from the SQL database, it is important that we also
# load its galaxy and queued orders from the JSON.
event.listen(Game, 'load', Game.on_load)
