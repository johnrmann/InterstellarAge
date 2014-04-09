"""
InterstellarAge
"""

# Import python modules
import random
import json

# Import the database
from interstellarage import db

# Define global variables
GALAXY_START_JSON = ""

SYSTEM_MIN_PLANETS = 1
SYSTEM_MAX_PLANETS = 10

class Galaxy(db.Model):
    """
    TODO
    """

    systems = []

    def __init__(self):
        """
        TODO
        """

        pass

    def as_list(self):
        """
        Returns:
            The contents of this `Galaxy` formatted as a `list`. This `list`
            can then be turned into JSON, which can be sent to the end user or
            written to a JSON file.
        """

        return [system.as_dict() for system in self.systems]

    def get_json_filename(self):
        """
        Returns the location of this Galaxy's JSON file on the filesystem.
        """

        pass



class System(object):
    """
    TODO
    """

    name = ""
    star_brightness = 0.0
    planets = []

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
            "star_brightness" : self.star_brightness,
            "planets" : [planet.as_dict() for planet in self.planets]
        }

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



class Planet(object):
    """
    TODO
    """

    name = ""
    moons = []

    space_colonies = []
    ground_colonies = []

    def __init__(self, layer, name=None, moons=None):
        """
        Args:
            layer (int): If we think of solar systems like trees where
                planets are nodes and moons are children, then the `layer` of
                a `Planet` is its depth in the tree. In the real world, Earth
                would have a layer of 1 and Luna a layer of 2. If the Moon had
                a moon, it would have a layer of 3.
            name (str): The name of this planet. If `None` is supplied, a
                random one will be created.
            moons (list of Planets):
        """

        pass

    def as_dict(self):
        return {
            "name" : self.name,
            "type" : self.__class__.__name__
            "moons" : [moon.as_dict() for moon in self.moons],
            "space_colonies" : [col.as_dict() for col in self.space_colonies],
            "ground_colonies" : [col.as_dict() for col in self.ground_colonies]
        }

    def _max_ground_colonies(self):
        return 0

    def _max_space_colonies(self):
        return 4

    def _random_name(self):
        self.name = "Delta Vega"



class GasPlanet(Planet):
    """
    TODO
    """

    def _max_ground_colonies(self):
        return 0

    def _max_space_colonies(self):
        return 4



class RockyPlanet(Planet):
    """
    Objects of this class reperesent planets that can be settled upon, but
    are not habitable. Real-life examples of such planets include Mars and
    Luna.
    """

    def _max_ground_colonies(self):
        return 4

    def _max_space_colonies(self):
        return 4



class HabitablePlanet(RockyPlanet):
    """
    TODO
    """

    def _max_ground_colonies(self):
        return 8

    def _max_space_colonies(self):
        return 4
