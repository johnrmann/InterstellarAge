"""
InterstellarAge
"""

# Import python modules
import random
import json
import pickle

# Import our modules
import system as system_lib

# Define constants.

# This is the path to the file of the default galaxy JSON. It contains the
# systems that spawn with every galaxy (such as the Solar System, Sirus, Alpha
# Centauri).
GALAXY_START_JSON = ""

# The grid distance (in grid spaces/lightyears) where the default systems end
# and procedurally generated systems begin.
GALAXY_DEFAULT_RANGE = 20
GALAXY_LENGTH = 125
GALAXY_WIDTH = 125
GALAXY_HEIGHT = 20

class Galaxy(object):
    """
    TODO
    """

    systems = []

    _planet_unique_counter = 0
    _system_unique_counter = 0

    def __init__(self, generate=False):
        """
        Keyword Args:
            game (Game):
        """

        # Escape gase.
        if not generate:
            return

        # Declare global variables.
        global GALAXY_START_JSON
        global GALAXY_DEFAULT_RANGE

        # Open the JSON
        json_f = open(GALAXY_START_JSON)
        json_contents = json_f.read()
        data = json.reads(json_contents)

        # Append default systems.
        for system in data:
            self._system_unique_counter += 1
            system_obj = system_lib.system_from_dict(system)
            system_obj.unique = _system_unique_counter

            # Assign the planets of this system unique identifiers
            system_planets = system_obj.flat_planets()
            
            self.systems.append(system_obj)



    def as_list(self, for_player=None):
        """
        Returns:
            The contents of this `Galaxy` formatted as a `list`. This `list`
            can then be turned into JSON, which can be sent to the end user or
            written to a JSON file.
        """

        return [system.as_dict() for system in self.systems]

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



def galaxy_from_json(json_str):
    data = json.loads(json_str)
    pass
