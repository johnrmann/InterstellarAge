# Import python modules
import json
import random

class Planet(object):
    """
    `Planet`s are objects contained in `System`s which `User`s fight to
    control. `Planet`s do two major things: (1) build starships and (2)
    generate money for `User`s at the beginning of every turn.

    Notes:
        - This should be considered an **abstract class**. It should **never
          be instantiated**. Instead, use one of its three subclasses:
          `GasPlanet`, `HabitablePlanet`, or `RockyPlanet`.

    Attributes:
        name (str):
        moons (list of Planet):
        parent (Planet or System): The body which the `Planet` orbits.

        space_colonies (list of SpaceColony):
        ground_colonies (list of GroundColony):

        owner (User or None):
        fleets (list of int):

    Private Attributes:
        _next_assign (int):
        _since_conquered (int): The number of turns since this `Planet` was
            conquered by another `User`.
    """

    name = ""
    moons = []
    parent = None

    space_colonies = []
    ground_colonies = []

    owner = None
    fleets = [0, 0, 0]

    _next_assign = 0
    _since_conquered = -1

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

    def economic_output(self):
        """
        Returns:
            `int` -- the economic output (in interstellar dollars) that this
            `Planet` produces every turn.
        """

        ground_output = len(self.ground_colonies) * self._max_ground_colonies()
        space_output = len(self.space_colonies) * self._max_space_colonies()

        return ground_output + space_output

    def fleet_departs(self, fleet_number):
        """
        Signifies that the fleet numbered `fleet_number` has left orbit of this
        `Planet`.

        Args:
            fleet_number (int): Should be less than the maximum number of
                fleets per planet.

        Returns:
            An `int` that is the number of starships in the fleet that left
            orbit of this `Planet`.
        """

        assert 0 <= fleet_number <= 2
        fleet_size = self.fleets[fleet_number]
        self.fleets[fleet_number] = 0
        return fleet_size

    def receive_fleet(self, incoming_fleet_size, from_user):
        """
        Args:
            incoming_fleet_size (int): A positive `int` -- the number of ships
                in the arriving navy.
            from_user (User): The `User` who sent the `MoveOrder` or
                `HyperspaceOrder` that sent the fleet to this `Planet`.

        Side-Effects:
            - If the `User` takes control of the `Planet`, then the `System` it
              is in is marked as being discovered by that `User`.

        TODO:
            - Space stations (`space_colonies`) might be part of combat --
              maybe add them in?
        """

        system = self.system()

        # Fleet sent to unoccupied planet
        if self.owner is None:
            self.fleets[0] = incoming_fleet_size
            self._next_assign = 1
            self.owner = from_user
            system.discover()

        # User sends fleet to owned planet
        elif from_user == self.owner:
            # Look for an empty fleet slot. If there is none, combine it with
            # an existing fleet.
            for a in xrange(0,3):
                if self.fleets[a] == 0:
                    self.fleets[a] = incoming_fleet_size
                    break
            else:
                self.fleets[self._next_assign] += incoming_fleet_size
                self._next_assign = (self._next_assign + 1) % 3

        # User sends fleet to planet owned by other player -- engage in
        # combat.
        else:
            for a in xrange(0,3):
                my_fleet = self.fleets[a]
                if my_fleet >= incoming_fleet_size:
                    self.fleets[a] -= incoming_fleet_size
                    break
                else:
                    incoming_fleet_size -= self.fleets[a]
                    self.fleets[a] = 0
            else:
                # If we reach this point, the invading user has won. Change
                # ownership.
                assert incoming_fleet_size > 0
                self.fleets = [incoming_fleet_size, 0, 0]
                self._next_assign = 1
                self.owner = from_user
                system.discover()

    def strength(self):
        """
        Returns:
            An `int` that is equal to the number of ships in the fleets
            orbiting this `Planet`.
        """

        return sum(self.fleets)

    def system(self):
        if isinstance(self.parent, System):
            return self.parent
        elif isinstance(self.parent, Planet):
            return self.parent.system()

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
    Objects of this class reperesent planets that are naturally suitable for
    human life. So far, Earth is the only real-life example of this sort of
    planet.
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
