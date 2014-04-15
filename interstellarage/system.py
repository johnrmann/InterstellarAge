"""
InterstellarAge
"""

# Import python modules
import random

# Define global variables.
DISCOVER_DISTANCE = 4

class System(object):
    """
    Attributes:
        name (str):
        position ( (int, int) ): The Cartesian position of this `System` in the
            Galaxy Map. A `position` of `(0, 0, 0)` represents the center square
            in the grid.
        star_brightness (float):
        planets (list of Planet): The `Planet`s in this `System`. Ordered such
            that the closest `Planet` to the star is at index 0.
        discovered_by (list of User): The `User`s that have discovered this
            `System`.
    """

    name = ""
    position = (0, 0, 0)
    star_brightness = 0.0
    planets = []
    discovered_by = set()

    galaxy = None

    def __init__(self, name, star_brightness=None, planets=None):
        """
        Args:
            name (str): The name of this system.
            star_brightness (float): 
            planets (list of Planets): The `Planet`s that form this system. If
                `None` is supplied instead of a list, then this system's
                `Planet`s will be randomly generated.
        """

        self.name = name
        if planets != None:
            self.planets = planets
            return

        # Randomly generate planets
        global SYSTEM_MIN_PLANETS
        global SYSTEM_MAX_PLANETS
        num_planets = random.randint(SYSTEM_MIN_PLANETS, SYSTEM_MAX_PLANETS)
        # TODO

    def as_dict(self):
        return {
            "name" : self.name,
            "x" : self.position[0],
            "y" : self.position[1],
            "z" : self.position[2],
            "star_brightness" : self.star_brightness,
            "planets" : [planet.as_dict() for planet in self.planets]
        }

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

    def discover(self, by_user):
        """
        Marks this `System` and all other `System`s nearby as having been
        discovered by the `User` "`by_user`".

        Args:
            by_user (User): The `User` that made the recent discovery.
        """

        global DISCOVER_DISTANCE
        self.discovered_by.add(by_user)
        for system in self.galaxy.systems_near_system(self, DISCOVER_DISTANCE):
            system.discovered_by.add(by_user)

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
            fleet_size (int):

        Returns:
            An `int` representing how many turns it will take a fleet of
            `fleet_size` ships to reach `other_system`.
        """

        return max(1, int(self.grid_distance(other_system) / 4))

    def receive_fleet(self, incoming_fleet_size, from_user):
        # Send the fleet to the nearset planet
        self.planets[-1].receive_fleet(incoming_fleet_size, from_user)
        self.discover()

    def _generate_planet(self, n):
        """
        Args:
            n (int):
        """

        chance_habitable = max(0.0, 0.1-((3-n)/10)**2)
        chance_rocky = max(0.0, 0.8-0.06*x)
        chance_gas = 1.0 - chance_habitable - chance_rocky

        roll = random.random()
        planet = None

        # Habitable planet
        if 0 <= roll < chance_habitable:
            pass

        # Rocky planet
        elif chance_habitable <= roll < chance_habitable + chance_rocky:
            pass

        # Gas planet
        else:
            pass

        return planet



def system_from_json(json):
    pass
