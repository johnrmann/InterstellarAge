"""
InterstellarAge
"""

# Import python modules
import random
import json
import pickle

# Import our modules
import system as system_lib

# Define global variables
GALAXY_START_JSON = ""

class Galaxy(object):
    """
    TODO
    """

    systems = []

    def __init__(self, game):
        """
        Args:
            game (Game):
        """

        # Declare global variables.
        global GALAXY_START_JSON

        # Open the JSON
        json_f = open(GALAXY_START_JSON)
        json_contents = json_f.read()
        data = json.reads(json_contents)

        # Append systems
        for system in data:
            self.systems.append()

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
