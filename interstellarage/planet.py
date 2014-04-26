"""
InterstellarAge
planet.py

Players vie for control of Planets in Interstellar Age. Planets allow Players
to build ships, found colonies, and dispatch fleets for expansion and invasion.

This module defines four classes: the `Planet` class is the abstract base class
for the `GasPlanet`, `HabitablePlanet`, and `RockyPlanet` classes. Gas planets
can only have colonies in space. Rocky planets can have colonies in space and
on the surface. Habitable planets can have colonies in space and twice as many
colonies on the surface.
"""

# Import python modules
import json
import random

# Import our stuff
from other import rand_float_range

# Define constants
ROCKY_PLANET_MIN_SIZE = 0.10
ROCKY_PLANET_MAX_SIZE = 5.00
HABITABLE_PLANET_MIN_SIZE = 0.50
HABITABLE_PLANET_MAX_SIZE = 2.50
GAS_PLANET_MIN_SIZE = 7.00
GAS_PLANET_MAX_SIZE = 20.00

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
        unique (int):
            Positive number uniquely identifying this `Planet`.

        name (str):
            The name of this `Planet`.

        moons (list of Planet):
            The `Planet`s that orbit this `Planet`.

        parent (Planet or System):
            The body which the `Planet` orbits.

        space_colonies (list of Colony):
            The `Colony`s that are in orbit of this `Planet`. Any type of
            planet can have up to four of these colonies.

        ground_colonies (list of Colony):

        owner (Player or None): The `Player` that last had a fleet above this
            `Planet` (if there is such a `Player`).

        fleets (list of int): The value `fleets[a]` is the number of starships
            in fleet number `a`.

        orbit_distance (float): The distance at which this planet orbits its
            parent. Measured in astronomical units (AU).

        orbit_period (float): The number of years it takes this planet to
            complete an orbit around its parent.

        size (float): The radius of this `Planet` in terms of multiples of
            Earth's radius.

        texture (str):
            The texture to be used for the 3D rendering of this planet.

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

    # Astronomy attributes.
    orbit_distance = 0.00
    orbit_period = 0.00
    size = 1.00
    texture = "earth.jpg"
    rings = None

    _next_assign = 0
    _since_conquered = -1

    def __init__(self, name=None, orbit_distance=None, min_size=0.0,
                 max_size=0.0):
        """
        This is the constructor for the `Planet` class. Since `Planet` is an
        abstract class, this constructor should never be called unless called
        by one of `Planet`'s three subclasses.

        Keyword Args:
            name (str):
                The name of the planet we're creating.

            orbit_distance (float):

            min_size (float);

            max_size (float):
        """

        # Preconditions.
        assert min_size != 0.0
        assert max_size != 0.0
        assert min_size < max_size

        # Assign name.
        if name is not None:
            self.name = name
        else:
            self.name = ""

        # Assign size.
        self.size = rand_float_range(min_size, max_size)

        # If we are given an orbit distance, then calculate an orbital period
        if orbit_distance is not None:
            self.orbit_distance = orbit_distance
            self.orbit_period = orbit_distance * rand_float_range(0.5, 1.5)
        else:
            self.orbit_distance = -1
            self.orbit_period = -1

    def __contains__(self, other):
        return other in self.moons

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
            "unique" : self.unique,
            "name" : self.name,
            "type" : self.__class__.__name__,
            "moons" : [moon.as_dict() for moon in self.moons],
            "space_colonies" : [col.as_dict() for col in self.space_colonies],
            "ground_colonies" : [col.as_dict() for col in self.ground_colonies],
            "owner" : owner_str,
            "fleets" : self.fleets,
            "orbit_distance" : self.orbit_distance,
            "orbit_period" : self.orbit_period,
            "size" : self.size,
            "texture" : self.texture,
            "rings" : self.rings
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
            incoming_fleet_size (int):
                A positive `int` -- the number of ships in the arriving navy.

            from_player (Player):
                The `Player` who sent the `MoveOrder` or `HyperspaceOrder`
                that sent the fleet to this `Planet`.

        Side-Effects:
            If the `Player` takes control of the `Planet`, then the `System`
            it is in is marked as being discovered by that `Player`.

        TODO:
            - Space stations (`space_colonies`) might be part of combat --
              maybe add them in?
            - If a planet is conquered, then maybe half of its colonies should
              disappear? There has to be some sort of penalty for annexation
              and occupation.
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

        # TODO
        return 100 * number

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
        """
        Returns:
            `int` -- the maximum number of colonies that can be on the ground
            of this planet at any point.
        """

        return 0

    def max_space_colonies(self):
        return 4

    def space_upgrade_cost(self):
        pass

    def ground_upgrade_cost(self):
        pass

    def valid(self):
        """
        Returns `True` if and only if this `Planet` is ready for the game.
        """

        # TODO
        if self.unique <= 0:
            return False
        return True



class GasPlanet(Planet):
    """
    Objects of this class represent planets that have super-thick atmospheres,
    leaving no possibility for any human settlement. Real-life examples of
    such planets include Saturn and Jupiter.

    `GasPlanet`s are the only type of planets that cannot have surface
    colonies (`ground_colonies`).
    """

    def __init__(self, name=None, orbit_distance=None):
        # Declare global variables.
        global GAS_PLANET_MAX_SIZE
        global GAS_PLANET_MIN_SIZE

        super(GasPlanet, self).__init__(
            name=name,
            orbit_distance=orbit_distance,
            min_size = GAS_PLANET_MIN_SIZE,
            max_size = GAS_PLANET_MAX_SIZE
        )

    def max_ground_colonies(self):
        """
        Returns:
            `int` -- the maximum number of colonies that can be on the ground
            of this planet at any point.
        """

        return 0

    def max_space_colonies(self):
        return 4

    def space_upgrade_cost(self):
        num_colonies = len(self.space_colonies)
        return 1000 * (1 + num_colonies)

    def ground_upgrade_cost(self):
        """
        Returns:
            `None` because `GasPlanet`s cannot have `Colony`s on their surface.
        """

        return None



class RockyPlanet(Planet):
    """
    Objects of this class reperesent planets that can be settled upon, but
    are not habitable. Real-life examples of such planets include Mars and
    Luna.
    """

    # Declare global variables.
    global ROCKY_PLANET_MAX_SIZE
    global ROCKY_PLANET_MIN_SIZE

    def __init__(self, name=None, orbit_distance=None,
                 min_size=ROCKY_PLANET_MIN_SIZE,
                 max_size=ROCKY_PLANET_MAX_SIZE):
        """
        Keyword Args:
            name (str):
                What we want to name the planet.

            orbit_distance (float):
                The distance at which this planet will orbit its parent (in
                AU).

            min_size (float):
                The minimum size that this planet can be. This arg should be
                considered *private* -- it may only be passed in by members of
                this module.

            max_size (float):
                The maxumum size that this planet can be. This arg should be
                considered *private* -- it may only be passed in by members of
                this module.
        """

        super(RockyPlanet, self).__init__(
            name=name,
            orbit_distance=orbit_distance,
            min_size=min_size,
            max_size=max_size
        )

    def max_ground_colonies(self):
        """
        Returns:
            `int` -- the maximum number of colonies that can be on the ground
            of this planet at any point.
        """
        return 4

    def max_space_colonies(self):
        return 4

    def space_upgrade_cost(self):
        num_colonies = len(self.space_colonies)
        return 1000 * (1 + num_colonies)

    def ground_upgrade_cost(self):
        num_colonies = len(self.ground_colonies)
        return 500 * (1 + num_colonies)



class HabitablePlanet(RockyPlanet):
    """
    Objects of this class reperesent planets that are naturally suitable for
    human life. So far, Earth is the only real-life example of this sort of
    planet.

    Due to their nice atmospheres and abundance of water, it costs less money
    to settle colonies on `HabitablePlanet`s.
    """

    def __init__(self, name=None, orbit_distance=None):
        # Declare global variables.
        global HABITABLE_PLANET_MAX_SIZE
        global HABITABLE_PLANET_MIN_SIZE

        super(HabitablePlanet, self).__init__(
            name=name,
            orbit_distance=orbit_distance,
            min_size = HABITABLE_PLANET_MIN_SIZE,
            max_size = HABITABLE_PLANET_MAX_SIZE
        )

    def max_ground_colonies(self):
        """
        Returns:
            `int` -- the maximum number of colonies that can be on the ground
            of this planet at any point.
        """
        return 8

    def max_space_colonies(self):
        return 4

    def space_upgrade_cost(self):
        num_colonies = len(self.space_colonies)
        return 750 * (1 + num_colonies)

    def ground_upgrade_cost(self):
        num_colonies = len(self.ground_colonies)
        return 250 * (1 + num_colonies)



class Colony(object):
    name = ""

    def __init__(self, name):
        self.name = name

    def as_dict(self):
        return {
            "name" : self.name
        }



def planet_from_dict(data, game):
    """
    Creates a `Planet` using infomration from a `dict` called `data`.

    Args:
        data (dict):
            The `dict` we want to parse.

        game (Game):
            The `Game` that this planet is part of.

    Returns:
        `Planet` -- a planet whose attributes match the provided `dict`.
    """

    planet = None

    # If the planet does not have a unique integer id, we assign "-1" as its
    # temporary value. If this happens, the planet *must* be assigned a unique
    # ID at some point before the game starts.
    if 'unique' in data:
        unique = int(data['unique'])
    else:
        unique = -1

    # Get basic information.
    name = data['name']
    moons = [planet_from_dict(moon, game) for moon in data['moons']]
    space = [colony_from_dict(col) for col in data['space_colonies']]
    if 'ground_colonies' in data:
        ground = [colony_from_dict(col) for col in data['ground_colonies']]
    else:
        ground = []
    fleets = data['fleets']

    # Get astronomy data
    orbit_distance = float(data['orbit_distance'])
    orbit_period = float(data['orbit_period'])
    size = float(data['size'])
    texture = data['texture']
    if 'rings' in data:
        rings = data['rings']
    else:
        rings = ""

    # Determine the type of planet to create.
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
    planet.space_colonies = space
    planet.ground_colonies = ground
    planet.fleets = fleets

    # Assign astronomy data.
    planet.orbit_distance = orbit_distance
    planet.orbit_period = orbit_period
    planet.size = size
    planet.texture = texture
    planet.rings = rings

    # Get the player's owner.
    planet.owner = game.player_for_faction(data['owner'])

    # We're done here.
    return planet



def colony_from_dict(data):
    return Colony(data['name'])
