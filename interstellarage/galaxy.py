"""
InterstellarAge
galaxy.py

This module defines the `Galaxy` class, which is used to contain the `System`s
and `Planet`s that `Player`s vie to control. It also defines several other
useful functions such as `generate_name`, which randomly creates a name.
"""

# Import python modules
import random
import json
import pickle

# Import our modules
import system as system_lib

# This is so we can bind URLs
from interstellarage import app

# Define constants.

# This is the path to the file of the default galaxy JSON. It contains the
# systems that spawn with every galaxy (such as the Solar System, Sirus, Alpha
# Centauri).
GALAXY_START_JSON = ""

# These constants are used for galaxy generation
STARS_PER_CUBIC_LY = (1 / (4 * 4 * 4))

# The grid distance (in grid spaces/lightyears) where the default systems end
# and procedurally generated systems begin.
GALAXY_DEFAULT_RANGE = 20
GALAXY_LENGTH = 125
GALAXY_WIDTH = 125
GALAXY_HEIGHT = 20

# The chance that a solar system won't have a name randomly generated from
# syllables.
CHANCE_SYSTEM_NAME = 0.5

# The minimum and maximum number of syllables a randomly-generated name can
# have.
NAME_MIN_SYLLABLES = 2
NAME_MAX_SYLLABLES = 5

# The maximum and minimum number of words a randomly-generated solar system
# name can have.
NAME_MIN_WORDS = 2
NAME_MAX_WORDS = 3

# Read the syllables.
SYLLABLES = ["herp", "derp"]

# Read the greek alphabet.
GREEK = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]

# Read the bayer words.
BAYER = ["Cygnus", "Vega"]

class Galaxy(object):
    """
    TODO
    """

    game = None
    systems = []

    _planet_unique_counter = 0
    _system_unique_counter = 0

    def __init__(self, game, generate=False):
        """
        Keyword Args:
            game (Game):
        """

        # Assign attributes.
        self.game = game

        # Escape gase.
        if not generate:
            return

        # Declare global variables.
        global GALAXY_START_JSON
        global GALAXY_DEFAULT_RANGE

        global GALAXY_LENGTH
        global GALAXY_WIDTH
        global GALAXY_HEIGHT

        global STARS_PER_CUBIC_LY

        # Open the JSON
        json_f = open(GALAXY_START_JSON)
        json_contents = json_f.read()
        data = json.reads(json_contents)

        # Append default systems.
        for system in data:
            # Parse the system dict and assign the system object a unique
            # ID.
            self._system_unique_counter += 1
            system_obj = system_lib.system_from_dict(system)
            system_obj.unique = self._system_unique_counter

            # Assign the planets of this system unique identifiers
            system_planets = system_obj.flat_planets()
            for planet in system_planets:
                self._planet_unique_counter += 1
                planet.unique = self._planet_unique_counter

            # Add the system to the galaxy
            self.systems.append(system_obj)

        # Creates inclusive range
        irange = lambda n, k: range(n, k+1)

        # The dimensions of the galaxy
        width = irange(-GALAXY_WIDTH, GALAXY_WIDTH)
        length = irange(-GALAXY_LENGTH, GALAXY_LENGTH)
        height = irange(-GALAXY_HEIGHT, GALAXY_HEIGHT)

        positions = [(x, y, z) for x in width for y in length for z in height]
        default_range = lambda x, y, z: (x + y + z <= GALAXY_DEFAULT_RANGE)

        # Loop through the galatic grid.
        generated = 0
        dice = 0
        for (x, y, z) in positions:
            dice = random.random()
            if default_range(x, y, z):
                continue

            # Generate a system.
            elif dice <= STARS_PER_CUBIC_LY:
                generated += 1
                self._system_unique_counter += 1
                new_sys = self._create_system(x, y, z)
                new_sys.unique = self._system_unique_counter

                # Assign the new planets unique identifiers.
                new_sys_planets = new_sys.flat_planets()
                for planet in new_sys_planets:
                    self._planet_unique_counter += 1
                    planet.unique = self._planet_unique_counter

                # Add the system to this galaxy.
                self.systems.append(new_sys)

        print "Generated {0} systems".format(str(generated))

    def as_list(self, for_player=None, for_user=None):
        """
        Returns:
            The contents of this `Galaxy` formatted as a `list`. This `list`
            can then be turned into JSON, which can be sent to the end user or
            written to a JSON file.
        """

        if for_user is not None:
            for player in self.game.players:
                if player.user == for_user:
                    for_player = player
                    break
            else:
                raise Exception("User doesn't have access")

        to_return = [system.as_dict() for system in self.systems]
        if for_player is not None:
            new_to_return = []
            for system in to_return:
                if for_player not in system.discovered_by:
                    continue
                new_to_return.append(system)
            return new_to_return
        return to_return

    def system_at_position(self, x, y, z):
        """
        Args:
            x (int): The x-coordinate to search for.
            y (int): Ditto.
            z (int): Ditto.

        Returns:
            `True` if and only if this `Galaxy` has a position whose
            coordinates match the given ones.
        """

        pos = (x, y, z)
        for system in self.systems:
            if system.position == pos:
                return True
        return False

    def systems_near_system(self, near_system, distance):
        """
        Returns:
        """

        return_systems = []
        for system in self.systems:
            if system == near_system:
                continue
            elif system.grid_distance(near_system) <= distance:
                return_systems.append(system)
        return return_systems

    def get_json_filename(self):
        """
        Returns the location of this Galaxy's JSON file on the filesystem.
        """

        pass

    def commit(self):
        """
        Compiles this format into one best for saving to disk and saves it.
        """

        to_save = self.as_list()
        fname = self.get_json_filename()

        # Open the file.
        galaxy_file = open(fname)
        pass

    def _create_system(self, x, y, z):
        """
        PRIVATE METHOD

        Args:
            x (int): The x-coordinate of where we want to make the new
                `System`.
            y (int): Ditto.
            z (int): Ditto.
        """

        # Generate a name for the system.
        system_name = _random_name(system=True)
        scheme = random.choice([1, 2]) # TODO
        system = system_lib.generate_system(system_name, scheme)
        system.position = (x, y, z)
        return system



def galaxy_from_json(json_str):
    data = json.loads(json_str)
    pass



def random_name(system=False):
    """
    Keyword Args:
        system (boolean): Set to `True` if we want to include "solar systemish"
            names such as "Epsilon Cygni" or "Tau Theta" in the name generation
            process. Set to `False` by default.

    Returns:
        `str` -- a randomly generated name.
    """

    # Declare global variables.
    global SYLLABLES
    global GREEK
    global BAYER
    global CHANCE_SYSTEM_NAME
    global NAME_MAX_SYLLABLES
    global NAME_MIN_SYLLABLES
    global NAME_MAX_WORDS
    global NAME_MIN_WORDS

    # We'll return this.
    name = ""

    # Decide just how exactly we're going to name this system.
    if system:
        dice = random.random()
        if dice <= CHANCE_SYSTEM_NAME:
            system = False

    # If we're going with syllables...
    if not system:
        sylls = random.randrange(NAME_MIN_SYLLABLES, NAME_MAX_SYLLABLES)
        for a in xrange(0, sylls):
            name += random.choice(SYLLABLES)

    # If we're going with system naming...
    else:
        pool = GREEK + BAYER
        words = random.randrange(NAME_MIN_WORDS, NAME_MAX_WORDS)
        for a in xrange(0, words):
            name += random.choice(pool)
            name += " "
        # Lop off the last spaces
        name = name[:-1]

    # We're done here.
    return name



@app.route('/game/galaxy/entire', methods=['POST'])
def web_entire_galaxy():
    # Get the current user.
    import user as user_lib
    user = user_lib.current_user()
    if user is None:
        return "Not logged in", 400

    # Get the desired game
    import game as game_lib
    game_unique = int(request.form['game'])
    game = game_lib.find(unique=game_unique)
    if game is None:
        return "Invalid game", 400
    elif user not in game:
        return "You are not part of this game", 400

    # Return the galaxy as JSON
    return json.dumps(game.galaxy.as_list(for_user=user))
