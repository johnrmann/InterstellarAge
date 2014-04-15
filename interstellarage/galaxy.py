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

    __tablename__ = 'galaxy'
    __table_args__ = {'extend_existing':True}

    unique = db.Column(db.Integer, primary_key=True)
    for_game = None
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
