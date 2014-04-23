# Import python modules
import json
import random

class Planet(object):
    """
    `Planet`s are objects contained in `System`s which `Player`s fight to
    control. `Planet`s do two major things: (1) build starships and (2)
    generate money for `Player`s at the beginning of every turn.

    Notes:
        - This should be considered an **abstract class**. It should **never
          be instantiated**. Instead, use one of its three subclasses:
          `GasPlanet`, `HabitablePlanet`, or `RockyPlanet`.

    Attributes:
        unique (int): Positive number uniquely identifying this `Planet`.

        name (str): The name of this `Planet`.
        moons (list of Planet): The `Planet`s that orbit this `Planet`.
        parent (Planet or System): The body which the `Planet` orbits.

        space_colonies (list of Colony):
        ground_colonies (list of Colony):

        owner (Player or None): The `Player` that last had a fleet above this
            `Planet` (if there is such a `Player`).
        fleets (list of int): The value `fleets[a]` is the number of starships
            in fleet number `a`.

        orbit_distance (float):
        orbit_period (float):
        size (float):
        texture (str): 
        rings (str or None): If the planet has rings (like Saturn), then
            `rings` is the filename of their texture. It is set to `None` if
            the planet does not have rings.

    Private Attributes:
        _next_assign (int):
        _since_conquered (int): The number of turns since this `Planet` was
            conquered by another `Player`.
    """

    unique = 0

    name = ""
    moons = []
    parent = None

    space_colonies = []
    ground_colonies = []

    owner = None
    fleets = [0, 0, 0]

    _next_assign = 0
    _since_conquered = -1

    def __init__(self, layer=None, name=None, moons=None):
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
        """
        Returns:
            Important data about this `Planet` encased in a `dict`. This `dict`
            can be used for saving game info to the server or sent back to the
            `Player`.
        """

        if self.owner is None:
            owner_str = ""
        else:
            owner_str = self.owner.faction_shortname()

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

        ground_output = len(self.ground_colonies) * self.max_ground_colonies()
        space_output = len(self.space_colonies) * self.max_space_colonies()

        return ground_output + space_output

    def flat_moons(self):
        """
        Returns:
            A one-dimensional `list` of `Planet`s in orbit of this `Planet` and
            the `Planet`s that would orbit those `Planet`s. In other words, if
            we think of a planetary system as a tree, this method returns the
            nodes in that tree (not including the root node).
        """

        to_return = []
        for moon in self.moons:
            to_return.append(moon)
            to_return.extend(moon.flat_moons())
        return to_return

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

    def receive_fleet(self, incoming_fleet_size, from_player):
        """
        Args:
            incoming_fleet_size (int): A positive `int` -- the number of ships
                in the arriving navy.
            from_player (Player): The `Player` who sent the `MoveOrder` or
                `HyperspaceOrder` that sent the fleet to this `Planet`.

        Side-Effects:
            - If the `Player` takes control of the `Planet`, then the `System`
              it is in is marked as being discovered by that `Player`.

        TODO:
            - Space stations (`space_colonies`) might be part of combat --
              maybe add them in?
        """

        system = self.system()

        # Fleet sent to unoccupied planet
        if self.owner is None:
            self.fleets[0] = incoming_fleet_size
            self._next_assign = 1
            self.owner = from_player
            system.discover()

        # Player sends fleet to owned planet
        elif from_player == self.owner:
            # Look for an empty fleet slot. If there is none, combine it with
            # an existing fleet.
            for a in xrange(0,3):
                if self.fleets[a] == 0:
                    self.fleets[a] = incoming_fleet_size
                    break
            else:
                self.fleets[self._next_assign] += incoming_fleet_size
                self._next_assign = (self._next_assign + 1) % 3

        # Player sends fleet to planet owned by other player -- engage in
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
                # If we reach this point, the invading player has won. Change
                # ownership.
                assert incoming_fleet_size > 0
                self.fleets = [incoming_fleet_size, 0, 0]
                self._next_assign = 1
                self.owner = from_player
                system.discover()

    def starship_build_cost(self, number):
        """
        Returns:
            An `int` equal to the price (in interstellar dollars) of building
            `number` starships above this `Planet`.
        """

        pass

    def strength(self):
        """
        Returns:
            An `int` that is equal to the number of ships in the fleets
            orbiting this `Planet`.
        """

        return sum(self.fleets)

    def system(self):
        """
        Returns:
            The `System` that contains this `Planet`.
        """
        
        if isinstance(self.parent, System):
            return self.parent
        elif isinstance(self.parent, Planet):
            return self.parent.system()

    def max_ground_colonies(self):
        return 0

    def max_space_colonies(self):
        return 4

    def _random_name(self):
        self.name = "Delta Vega"



class GasPlanet(Planet):
    """
    TODO
    """

    def max_ground_colonies(self):
        return 0

    def max_space_colonies(self):
        return 4



class RockyPlanet(Planet):
    """
    Objects of this class reperesent planets that can be settled upon, but
    are not habitable. Real-life examples of such planets include Mars and
    Luna.
    """

    def max_ground_colonies(self):
        return 4

    def max_space_colonies(self):
        return 4



class HabitablePlanet(RockyPlanet):
    """
    Objects of this class reperesent planets that are naturally suitable for
    human life. So far, Earth is the only real-life example of this sort of
    planet.
    """

    def max_ground_colonies(self):
        return 8

    def max_space_colonies(self):
        return 4



class Colony(object):
    name = ""

    def as_dict(self):
        return {
            "name" : self.name
        }



def planet_from_dict(data, game):
    """
    Creates a `Planet` using infomration from a `dict` called `data`.

    Args:
        data (dict):
        game (Game):
    """

    planet = None

    unique = data['unique']
    name = data['name']
    moons = [planet_from_dict(moon, game) for moon in data['moons']]
    space_colonies = [colony_from_dict(col) for col in data['space_colonies']]
    ground_colonies = [colony_from_dict(col) for col in data['ground_colonies']]
    fleets = data['fleets']

    if data['type'] == 'GasPlanet':
        planet = GasPlanet()
    elif data['type'] == 'RockyPlanet':
        planet = RockyPlanet()
    elif data['type'] == 'HabitablePlanet':
        planet = HabitablePlanet()
    else:
        raise Exception("Unknown planet type {0}".format(data['type']))

    # Do final setup.
    for moon in moons:
        moon.parent = planet

    # Assign the data to the planet.
    planet.unique = unique
    planet.name = name
    planet.moons = moons
    planet.space_colonies = space_colonies
    planet.ground_colonies = ground_colonies
    planet.fleets = fleets

    # Get the player's owner.
    planet.owner = game.player_for_faction(data['owner'])

    # We're done here.
    return planet



def colony_from_dict(data):
    return Colony(data['name'])
