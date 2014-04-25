"""
InterstellarAge
"""

# Import python modules
import random

# Import InterstellarAge modules.
import planet as planet_lib

# Define global variables.
DISCOVER_DISTANCE = 4
SYSTEM_MIN_PLANETS = 1
SYSTEM_MAX_PLANETS = 10

SYSTEM_SCHEME_SYLLABLES = 1
SYSTEM_SCHEME_STAR = 2

SPECTRAL_CLASSES = ["O", "B", "A", "F", "G", "K", "M", "L", "T", "Y"]

class System(object):
    """
    Attributes:
        unique (int): Unique identifier for this `System` within the context of
            the current `Game`.

        name (str):
        position ( (int, int) ): The Cartesian position of this `System` in the
            Galaxy Map. A `position` of `(0, 0, 0)` represents the center square
            in the grid.

        star_size (float): The radius of the star in terms of the radius of our
            sun.
        star_spectral_class (str): The spectral class of this system's star. An
            example: our sun is spectral class G2V.

        planets (list of Planet): The `Planet`s in this `System`. Ordered such
            that the closest `Planet` to the star is at index 0.

        discovered_by (set of Player): The `Player`s that have discovered this
            `System` (able to travel to it).
        planets_discovered_by (set of Player): The `Player`s that are able to
            travel to specific `Planet`s in this `System`. This value is
            always a subset of `discovered_by`.

        galaxy (Galaxy): The `Galaxy` that contains this `System`.
    """

    unique = 0

    name = ""
    position = (0, 0, 0)

    star_spectral_class = ""
    star_size = 0.0

    planets = []

    discovered_by = set()
    planets_discovered_by = set()

    galaxy = None

    def __init__(self, name, star_spectral_class=None, generate_planets=False):
        """
        Args:
            name (str): The name of this system.

        Postconditions:
            If a `star_spectral_class` was given, then a `star_size` will also
            be calculated.
        """

        self.name = name
        
        if star_spectral_class is not None:
            self.star_spectral_class = star_spectral_class
            # TODO set size

    def __contains__(self, other):
        """
        Returns `True` if and only if the given `Planet` we call `other` is
        inside this `System`.
        """

        return other in self.planets

    def as_dict(self, hide_planets=False, include_discoveries=True):
        """
        Keyword Args:
            hide_planets (boolean): Set to `True` if an empty list is to be
                returned in the "planets" field of the `dict`. A situation
                where this is necessary is if the `Player` has not discovered
                the `Planet`s in this `System` yet.

            include_discoveries (boolean): Set to `True` if we are to include
                information about the `Player`s that have discovered this
                `System` with the return `dict`.

        Returns:
            Important data about this `System` encased in a `dict`. This `dict`
            can be used for saving game info to the server or sent back to the
            `Player`.
        """

        to_return = {
            "unique" : self.unique,
            "name" : self.name,
            "x" : self.position[0],
            "y" : self.position[1],
            "z" : self.position[2],
            "star_size" : self.star_size,
            "star_spectral_class" : self.star_spectral_class,
            "planets" : [planet.as_dict() for planet in self.planets]
        }

        if hide_planets:
            to_return['planets'] = []

        if include_discoveries:
            faction = lambda p: p.faction_shortname()
            star = [faction(p) for p in self.discovered_by]
            planets = [faction(p) for p in self.planets_discovered_by]
            to_return['discovered_by'] = star
            to_return['planets_discovered_by'] = planets

        return to_return

    def cartesian_distance(self, other_system):
        """
        Args:
            other_system (System):

        Return:
            A `float` representing the cartesian distance between the two
            `System`s.
        """

        my_x = self.position[0]
        my_y = self.position[1]
        my_z = self.position[2]
        other_x = other_system.position[0]
        other_y = other_system.position[1]
        other_z = other_system.position[2]

        x = abs(my_x - other_x)
        y = abs(my_y - other_y)
        z = abs(my_z - other_z)

        import math
        return math.sqrt(x**2 + y**2 + z**2)

    def discover(self, by_player):
        """
        When a fleet from a `Player` (in this case, called `by_player`) arrives
        at a `System` for the first time, the `Planet`s in that `System` are
        marked as "discovered". This means that from that point forward,
        `by_player` can plot hyperspace jumps directly to the planets of this
        `System` instead of to the `System` in genreal.

        This method also marks all `System`s within a certain range of this one
        (but not their planets) as having been discovered, meaning they will be
        visible on the Galaxy Map.

        Args:
            by_player (Player): The `Player` that made the recent discovery.
        """

        global DISCOVER_DISTANCE
        self.planets_discovered_by.add(by_player)
        for system in self.galaxy.systems_near_system(self, DISCOVER_DISTANCE):
            system.discovered_by.add(by_player)

    def flat_planets(self):
        """
        Returns:
            A `list` of the `Planet`s in this `System` and the `Planet`s that
            are moons of those `Planet`s. In other words: think of a solar
            system as a tree with the sun being the root node, planets being
            leafs, and moons being the leafs of planets. This method returns
            all leafs in the tree in a one-dimensional list (not including
            the root node).
        """

        to_return = []
        for planet in self.planets:
            to_return.append(planet)
            to_return.extend(planet.flat_moons())
        return to_return

    def grid_distance(self, other_system):
        """
        Args:
            other_system (System):

        Returns:
            An `int` representing the grid distance between the two `System`s.
        """

        my_x = self.position[0]
        my_y = self.position[1]
        my_z = self.position[2]
        other_x = other_system.position[0]
        other_y = other_system.position[1]
        other_z = other_system.position[2]

        x = abs(my_x - other_x)
        y = abs(my_y - other_y)
        z = abs(my_z - other_z)

        return x + y + z

    def hyperspace_jump_length(self, other_system, fleet_size):
        """
        Args:
            other_system (System):
            fleet_size (int): The number of ships in the departing fleet.

        Returns:
            An `int` representing how many turns it will take a fleet of
            `fleet_size` ships to reach `other_system`.
        """

        return max(1, int(self.grid_distance(other_system) / 4))

    def receive_fleet(self, incoming_fleet_size, from_player):
        # Ensure data structure invariants
        assert from_player not in self.planets_discovered_by
        assert from_player in self.discovered_by

        # Send the fleet to the nearset planet
        self.planets[-1].receive_fleet(incoming_fleet_size, from_player)
        self.discover()

    def owners(self):
        """
        Returns:
            The `set` of `Player`s who occupy at least one `Planet` in this
            `System`.
        """

        all_planets = self.flat_planets()
        to_return = set()
        for planet in all_planets:
            to_return.add(planet.owner)
        return to_return



def generate_system(name, scheme):
    """
    Returns:
        A `System` generated at random.
    """

    # Declare global variables.
    global SYSTEM_MAX_PLANETS
    global SYSTEM_MIN_PLANETS

    # How many planets does this system have?
    num_planets = random.randint(SYSTEM_MIN_PLANETS, SYSTEM_MAX_PLANETS)

    # Generate a random spectral class.
    star_spectral_class = _random_spectral_class()

    # Now calculate the maximum and minimum distances planets can be between.
    min_orbit_dist = 0.1
    max_orbit_dist = 30.0 # TODO

    # Calculate the orbiting distances between the planets.
    orbit_distances = []
    for a in xrange(0, num_planets):
        distance = random.randrange(min_orbit_dist, max_orbit_dist)
        orbit_distances.append(distance)
    orbit_distances.sort()

    # This is the probability of a planet being rocky as a function of its
    # orbital distance from its star.
    chance_rocky = lambda d: 0.5 # TODO

    # This is the probability of a planet being habitable GIVEN that it is
    # rocky as a function of its orbital distance.
    chance_habitable = lambda d: 0.25 # TODO

    # Begin creating the planets
    planets = []
    a = 1 # used for iteration
    for distance in orbit_distances:
        planet = None
        dice = random.random()

        # Case: Rocky or habitable planet
        if dice <= chance_rocky(distance):
            # Case: Habitable planet
            dice = random.random()
            if dice <= chance_habitable(distance):
                planet = planet_lib.HabitablePlanet(orbit_distance=distance)

            # Case: Rocky planet
            else:
                planet = planet_lib.RockyPlanet(orbit_distance=distance)

        # Case: Gas Planet
        else:
            planet = planet_lib.GasPlanet(orbit_distance=distance)

        # TODO setup planet
        planet.name = _planet_name(name, scheme, a)
        planets.append(planet)
        a += 1

    # Setup the system that we will return
    system = System(name, star_spectral_class=star_spectral_class)



def system_from_dict(data, game):
    # Find the unique.
    if 'unique' in data:
        unique = int(data['unique'])
    else:
        unique = -1

    # Get data from the dictionary.
    name = data['name']
    x = int(data['x'])
    y = int(data['y'])
    z = int(data['z'])
    star_size = float(data['star_size'])
    star_spectral_class = data['star_spectral_class']
    planets = [planet_lib.planet_from_dict(p, game) for p in data['planets']]

    # Setup the system.
    system = System(
        name,
        star_spectral_class=star_spectral_class
    )
    system.unique = unique
    system.planets = planets
    system.star_size = star_size
    system.position = (x, y, z)
    system.galaxy = game.galaxy

    # We're done here.
    return system



def _random_spectral_class():
    global SPECTRAL_CLASSES
    return random.choice(SPECTRAL_CLASSES)



def _planet_name(system_name, scheme, n):
    # Import required modules.
    import galaxy as galaxy_lib
    from other import int_to_roman

    # Define global variables.
    global SYSTEM_SCHEME_STAR
    global SYSTEM_SCHEME_SYLLABLES

    # Case: named after star
    if scheme == SYSTEM_SCHEME_STAR:
        return system_name+" "+int_to_roman(n)

    # Case: random name
    else:
        return galaxy_lib.generate_name()
