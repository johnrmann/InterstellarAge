# Import python modules
import json
import random

# Import InterstellarAge modules.
from user import User
from system import System
from galaxy import Galaxy

class Planet(object):
    """
    TODO
    """

    name = ""
    moons = []
    parent = None

    space_colonies = []
    ground_colonies = []

    owner = None
    fleets = [0, 0, 0]

    _next_assign = 0

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
        if self.owner is None:
            owner_str = None
        else:
            owner_str = "ISCA" # TODO

        parent_str = "" # TODO

        return {
            "name" : self.name,
            "type" : self.__class__.__name__,
            "moons" : [moon.as_dict() for moon in self.moons],
            "space_colonies" : [col.as_dict() for col in self.space_colonies],
            "ground_colonies" : [col.as_dict() for col in self.ground_colonies],
            "owner" : owner_str,
            "fleets" : self.fleets
        }

    def strength(self):
        return sum(self.fleets)

    def system(self):
        if isinstance(self.parent, System):
            return self.parent
        elif isinstance(self.parent, Planet):
            return self.parent.system()

    def fleet_departs(self, fleet_number):
        assert 0 <= fleet_number <= 2
        fleet_size = self.fleets[fleet_number]
        self.fleets[fleet_number] = 0
        return fleet_size

    def receive_fleet(self, incoming_fleet_size, from_user):
        if from_user == self.owner:
            # Look for an empty fleet slot. If there is none, combine it with
            # an existing fleet.
            for a in xrange(0,3):
                if self.fleets[a] == 0:
                    self.fleets[a] = incoming_fleet_size
                    break
            else:
                self.fleets[self._next_assign] += incoming_fleet_size
                self._next_assign = (self._next_assign + 1) % 3
        else:
            for a in xrange(0,3):
                my_fleet = self.fleets[a]
                if my_fleet >= incoming_fleet_size:
                    self.fleets[a] -= incoming_fleet_size
                    return
                else:
                    incoming_fleet_size -= self.fleets[a]
                    self.fleets[a] = 0
            # If we reach this point, the invading user has won. Change
            # ownership.
            assert incoming_fleet_size > 0
            self.fleets = [incoming_fleet_size, 0, 0]
            self._next_assign = 1
            self.owner = from_user

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



class Colony(object):
    name = ""

    def as_dict(self):
        return {
            "name" : self.name
        }



class SpaceColony(Colony):
    pass



class GroundColony(Colony):
    pass
