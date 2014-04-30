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

# Import Flask
from flask import request

# This is so we can bind URLs
from interstellarage import app

# Import other useful things
from other import coinflip, irange

# Define constants.

# This is the path to the file of the default galaxy JSON. It contains the
# systems that spawn with every galaxy (such as the Solar System, Sirus, Alpha
# Centauri).
GALAXY_START_JSON = "/static/json/default_galaxy.json"

# These constants are used for galaxy generation
STARS_PER_CUBIC_LY = (1.0 / (4.0 * 4.0 * 4.0))

# The grid distance (in grid spaces/lightyears) where the default systems end
# and procedurally generated systems begin.
GALAXY_DEFAULT_RANGE = 20
GALAXY_LENGTH = 101
GALAXY_WIDTH = 101
GALAXY_HEIGHT = 21

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
    For every `Game` being played, there is one and only one `Galaxy`
    associated with that `Game`. `Galaxy`s contain `System`s, which contain
    `Planet`s, which are the whole purpose behind the game.

    Attributes:
        game (Game):
            The game associated with this `Galaxy`.

        systems (list of System):
            The `System`s in this `Galaxy`.

    Private Attributes:
        _planet_unique_counter (int):
            This attribute is incremented every time a new planet is created in
            this `Galaxy`. This way, every `Planet` is assigned a unique `int`
            in its `unique` field.

        _system_unique_counter (int):
            This attribute is incremented every time a new system is created in
            this `Galaxy`. This way, every `System` is assigned a unique `int`
            in its `unique` field.
    """

    game = None
    systems = []

    _planet_unique_counter = 0
    _system_unique_counter = 0

    def __init__(self, game, generate=False):
        """
        Not only is this the constructor for the `Galaxy` class, this also will
        generate a random `Galaxy` if and only if the correct and precise
        keyword arguments are passed in (hint: to generate a `Galaxy`, set
        `generate` to `True`).

        Args:
            game (Game):
                The `Game` which this `Galaxy` will be used for.

        Keyword Args:
            generate (boolean):
                Set to `True` if this `Galaxy` is to be generated at random.

        Note:
            It is the responsibility of the caller of this constructor to save
            this galaxy to disk.
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
        import os
        current_directory = os.path.dirname(__file__)
        json_f = open(current_directory+GALAXY_START_JSON)
        json_contents = json_f.read()
        data = json.loads(json_contents)
        json_f.close()

        # Append default systems.
        for system in data:
            # Parse the system dict and assign the system object a unique ID.
            self._system_unique_counter += 1
            system_obj = system_lib.system_from_dict(system, game)
            system_obj.unique = self._system_unique_counter
            system_obj.galaxy = self

            # Assign the planets of this system unique identifiers
            system_planets = system_obj.flat_planets()
            for planet in system_planets:
                self._planet_unique_counter += 1
                planet.unique = self._planet_unique_counter

            self.systems.append(system_obj)

        # The dimensions of the galaxy.
        adj_dim = lambda x: (x - 1) / 2
        abs_sum = lambda x, y, z: abs(x) + abs(y) + abs(z)
        width = irange(-adj_dim(GALAXY_WIDTH), adj_dim(GALAXY_WIDTH))
        length = irange(-adj_dim(GALAXY_LENGTH), adj_dim(GALAXY_LENGTH))
        height = irange(-adj_dim(GALAXY_HEIGHT), adj_dim(GALAXY_HEIGHT))

        positions = [(x, y, z) for x in width for y in length for z in height]
        gdr = GALAXY_DEFAULT_RANGE
        in_default_range = lambda x, y, z: (abs_sum(x, y, z) <= gdr)
        in_discover_range = lambda x, y, z: (abs_sum(x, y, z) <= gdr + 4)

        # Loop through the galatic grid. For the positions outside the range of
        # default systems, randomly create new ones.
        generated = 0
        for (x, y, z) in positions:
            if in_default_range(x, y, z):
                continue
            elif coinflip(STARS_PER_CUBIC_LY):
                generated += 1
                self._system_unique_counter += 1
                new_sys = self._create_system(x, y, z)
                new_sys.unique = self._system_unique_counter

                if in_discover_range(x, y, z):
                    new_sys.discovered_by = set(game.players)

                # Assign the new planets unique identifiers.
                new_sys_planets = new_sys.flat_planets()
                for planet in new_sys_planets:
                    self._planet_unique_counter += 1
                    planet.unique = self._planet_unique_counter

                self.systems.append(new_sys)

        # Save to disk
        print "Generated {0} systems".format(str(generated))

    def as_list(self, for_player=None, for_user=None, discoveries=False):
        """
        Keyword Args:
            for_player (Player):
                If this information is to be returned to an end user, then
                `for_player` should be set to said end user's `Player` object
                for the current game.

            for_user (User):
                If no `Player` object is readily available, then `for_user` may
                be used instead.

            discoveries (boolean):
                Set to `False` by default. Set to `True` if information about
                the factions that have discovered the systems is to be included
                in the returned list.

        Returns:
            The contents of this `Galaxy` formatted as a `list`. This `list`
            can then be turned into JSON, which can be sent to the end user or
            written to a JSON file.
        """

        # If we were supplied a User instead of a Player, get the player for
        # that user.
        if for_user is not None:
            for_player = self.game.player_for_user(for_user)

        # This helper function returns "True" if the player in question can
        # plot hyperspace routes to the system. If no player is provided, then
        # the system is always visible.
        def can_see_system(s):
            if for_player is None:
                return True
            else:
                return for_player in s.discovered_by

        # This helper function returns "True" if the player in question can
        # send fleets to specific planets in the system. If no player is
        # provided, then the planets are always visible.
        def can_see_planets(s):
            if for_player is None:
                return True
            else:
                return for_player in s.planets_discovered_by

        return_systems = []
        for system in self.systems:
            if not can_see_system(system):
                continue
            system_dict = system.as_dict(
                hide_planets=(not can_see_planets(system)),
                include_discoveries=discoveries
            )
            return_systems.append(system_dict)

        return return_systems

    def planet_for_unique(self, unique):
        """
        Args:
            unique (int):

        Returns:
            The `Planet` in this `Galaxy` whose unique ID matches the provided
            one or `None` if no such `Planet` was found.
        """

        for system in self.systems:
            all_planets = system.flat_planets()
            for planet in all_planets:
                if planet.unique == unique:
                    return planet
        return None

    def system_at_position(self, x, y, z):
        """
        Args:
            x (int):
                The x-coordinate to search for.

            y (int):
                Ditto.

            z (int):
                Ditto.

        Returns:
            `True` if and only if this `Galaxy` has a position whose
            coordinates match the given ones.
        """

        pos = (x, y, z)
        for system in self.systems:
            if system.position == pos:
                return True
        return False

    def system_for_unique(self, unique):
        """
        Args:
            unique (int):

        Returns:
            The `System` whose `System.unique` attribute matches `unique` or
            `None` if no such `System` in this `Galaxy` exists.
        """

        for system in self.systems:
            if system.unique == unique:
                return system
        return None

    def systems_near_system(self, near_system, distance):
        """
        Args:
            near_system (System):

            distance (int):
                The search radius (in grid spaces).

        Returns:
            The `list` of all `System`s in this `Galaxy` that are within
            `distance` grid spaces of `near_system`. This `list` does not
            include `near_system`.
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

        return "{0}.galaxy.json".format(str(self.game.unique))

    def _create_system(self, x, y, z):
        """
        PRIVATE METHOD

        Args:
            x (int):
                The x-coordinate of where we want to make the new `System`.

            y (int):
                Ditto.

            z (int):
                Ditto.

        Returns:
            A new `System`.
        """

        # Generate a name for the system.
        system_name = random_name(system=True)
        scheme = random.choice([1, 2]) # TODO
        system = system_lib.generate_system(system_name, scheme)
        system.position = (x, y, z)
        system.galaxy = self
        assert system is not None
        return system



def galaxy_from_dict(data, game):
    """
    Creates the `Galaxy` for `game` from the `dict` `data`.

    Args:
        data (list):
            The list of `System` dictionaries.

        game (Game):
            The `Game` that the `Galaxy` is used for.

    Returns:
        The `Galaxy` that was parsed from the given `dict` and `Game`.
    """

    systems = []
    for system_dict in data:
        system = system_lib.system_from_dict(system_dict, game)
        systems.append(system)

    # Create the galaxy and return it.
    galaxy = Galaxy(game)
    galaxy.systems = systems
    return galaxy



def random_name(system=False):
    """
    Generates a name. These names can be used for planets or solar systems.
    Names more suited for solar systems can be generated if `system` is set to
    `True`.

    Keyword Args:
        system (boolean):
            Set to `True` if we want to include "solar systemish" names such
            as "Epsilon Cygni" or "Tau Theta" in the name generation process.
            Set to `False` by default.

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
        # Lop off the last space.
        name = name[:-1]

    # We're done here.
    return name



@app.route('/game/galaxy/entire', methods=['POST'])
def web_entire_galaxy():
    """
    This function is called when the client needs to update its local galaxy
    information. This method therefore reads outputs the `Galaxy` dict as JSON
    along with some other useful information such as funds available and
    current turn number.

    Request Fields:
        game (int):
            The unique id for the game that is being played.

    Returns:
        A JSON `str` including the JSON for the galaxy in the "galaxy" field,
        the amount of money the player has in the "money" field, and the game's
        turn number in the "turn" field.
    """

    # Get the current user.
    from interstellarage import current_user
    user = current_user()
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
    return json.dumps({
        'galaxy' : game.galaxy.as_list(for_user=user),
        'turn' : game.on_turn,
        'money' : game.player_for_user(user).money
    })
