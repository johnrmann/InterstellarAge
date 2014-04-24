"""
InterstellarAge
orders.py

Orders are executed in the following order:
    1) Colonies are built
    2) Fleets depart planets
    3) Fleets are built
    4) Fleets arrive at intrasystem planets
    5) Fleets arrive at hyperspace planets
"""

# Import python modules.
import json

# Import TODO
from interstellarage import app, db

# Import our modules
import planet as planet_lib
import system as system_lib

# Define global variables
ORDER_NOT_FINISHED = 0
ORDER_NEXT_TURN = 1
ORDER_NOT_FINISHED_NEXT_TURN = 2
ORDER_FAILED = 3

ORDER_UPGRADE_GROUND_TYPE = 1
ORDER_UPGRADE_SPACE_TYPE = 2

class Order(object):
    orderer = None
    _phase = 0

    def execute(self, galaxy):
        pass



class Result(object):
    """
    Attributes:
        planet (Planet):

        new_owner (Player or None):

        new_fleets (list of 3 int or None): If the fleets of `planet` have
            changed, then `new_fleet` will be a `list` representing the new
            fleets. Otherwise, it will be `None`.

        new_space_colonies (list of str or None): If the 

        new_ground_colonies (list of str or None):
    """

    # Required data
    planet = None

    # Optional data
    new_owner = None
    new_fleets = None
    new_space_colonies = None
    new_ground_colonies = None

    def __init__(self, planet):
        assert planet is not None
        self.planet = planet

    def as_dict(self):
        unique = self.planet.unique
        to_return = {
            'planet_unique' : unique
        }

        f = lambda name: {'name' : name}

        if self.new_owner is not None:
            to_return['new_owner'] = self.new_owner.faction_shortname()

        if self.new_fleets is not None:
            to_return['new_fleets'] = self.new_fleets

        if self.new_space_colonies is not None:
            cols = self.new_space_colonies
            to_return['new_space_colonies'] = [f(name) for name in cols]

        if self.new_ground_colonies is not None:
            cols = self.new_ground_colonies
            to_return['new_ground_colonies'] = [f(name) for name in cols]

        return to_return



class MoveOrder(Order):
    """
    Attributes:
        orderer (Player): The `Player` that issued the orders.
        to_planet (Planet): The destination of the fleet.
        from_planet (Planet): The origin of the fleet.
        fleet_number (int): Signifies that we are moving fleet number n.

    Private Attributes:
        _phase (int): 

        _fleet_size (int): The number of ships in the fleet that this
            `MoveOrder` is supposed to move.

        _from_result (Result):

        _to_result (Result):
    """

    to_planet = None
    from_planet = None
    fleet_number = -1

    _fleet_size = -1

    _from_result = None
    _to_result = None

    def __init__(self, orderer, from_planet, to_planet, fleet_number):
        # Preconditions.
        assert orderer is not None
        assert from_planet is not None
        assert to_planet is not None
        assert from_planet.owner == orderer
        assert 0 <= fleet_number <= 2

        # Assign data
        self.orderer = orderer
        self.from_planet = from_planet
        self.to_planet = to_planet
        self.fleet_number = fleet_number
        self._phase = 1
        self._from_result = Result(self.from_planet)
        self._to_result = Result(self.to_planet)

        # Setup results
        self._from_result.new_fleets = self.from_planet.fleets

    def execute(self, galaxy):
        """
        Returns:
        """

        # Declare global variables.
        global ORDER_NOT_FINISHED
        global ORDER_NEXT_TURN

        # Ensure data structure invaraints.
        assert self.from_planet in galaxy
        assert self.to_planet in galaxy

        # PHASE 1: Colonies built
        if self._phase == 1 or self._phase == 3:
            self._phase += 1
            return ORDER_NOT_FINISHED

        # PHASE 2: Fleets leave their planet.
        if self._phase == 2:
            fleet_size = self.from_planet.fleet_departs(self.fleet_number)
            assert fleet_size > 0

            # Update from result
            self._from_result.new_fleets[self.fleet_number] = 0

            # Update variables
            self._fleet_size = fleet_size
            self._phase = 3
            return ORDER_NOT_FINISHED

        # PHASE 4: Fleets arrive at destination. They do combat if required.
        elif self._phase == 4:
            fs = self._fleet_size
            self.to_planet.receive_fleet(fs, self.orderer)
            return ORDER_NEXT_TURN



class HyperspaceOrder(Order):
    from_planet = None
    fleet_number = -1
    to_planet = None
    to_system = None

    _eta = -1

    def __init__(self, orderer, from_planet, dest, fleet_number):
        """
        Args:
            orderer (Player):
            from_planet (Planet):
            dest (Planet or System):
            fleet_number (int):
        """

        # Preconditions.
        assert orderer is not None
        assert from_planet is not None
        assert dest is not None
        assert 0 <= fleet_number <= 2

        # Assign data
        self.orderer = orderer
        self.from_planet = from_planet
        if isinstance(dest, planet_lib.Planet):
            self.to_planet = dest
        else:
            self.to_system = dest
        self.fleet_number = fleet_number
        self._phase = 1

    def execute(self, galaxy):
        # Declare global variables.
        global ORDER_NOT_FINISHED
        global ORDER_NEXT_TURN
        global ORDER_NOT_FINISHED_NEXT_TURN

        # Ensure data structure invariants.
        assert self.from_planet in galaxy
        assert self.to_planet in galaxy or self.to_system in galaxy
        assert self.from_planet.owner == self.orderer
        assert 0 <= self.fleet_number <= 2

        if self.to_system is None:
            assert self.to_planet is not None
            self.to_system = self.to_planet.system()

        # PHASE 1: Colonies are build
        if self._phase == 1:
            self._phase = 2
            return ORDER_NOT_FINISHED

        # PHASE 2: Fleets depart planets
        if self._phase == 2:
            from_system = self.from_planet.system()

            fleet_size = self.from_planet.fleet_departs(self.fleet_number)
            assert fleet_size > 0
            self._fleet_size = fleet_size

            eta = from_system.hyperspace_distance(self.to_system, fleet_size)
            self._eta = eta
            self._phase = 3
            return ORDER_NOT_FINISHED

        # PHASE 3: Fleets are built
        if self._phase == 3:
            self._phase = 4
            return ORDER_NOT_FINISHED

        # PHASE 4: Fleets arrive at intrasystem destinations
        elif self._phase == 4:
            self._phase = 5
            return ORDER_NOT_FINISHED_NEXT_TURN

        # PHASE 5: Hyperspace travel
        elif self._phase == 5:
            self._eta -= 1
            if self._eta == 0:
                if self.to_planet is not None:
                    self.to_planet.receive_fleet(self._fleet_size, self.orderer)
                else:
                    self.to_system.receive_fleet(self._fleet_size, self.orderer)
                return ORDER_NEXT_TURN
            else:
                return ORDER_NOT_FINISHED_NEXT_TURN



class UpgradePlanetOrder(Order):
    """
    `Order`s of this type are issued when a `Player` wants to found a new
    `Colony` on a `Planet` either in space or on the ground.

    Attributes:
        planet_to_upgrade (Planet): The `Planet` where the `Colony` will
            be built.
        upgrade_type (int):
        new_colony_name (str): What we want to name the new `Colony`.
    """

    planet_to_upgrade = None
    upgrade_type = 0
    new_colony_name = ""

    def __init__ (self, orderer, planet, up_type, name):
        # Preconditions.
        cond1 = up_type == ORDER_UPGRADE_SPACE_TYPE
        cond2 = up_type == ORDER_UPGRADE_GROUND_TYPE
        assert planet is not None
        assert planet.owner == orderer
        assert len(name) >= 1
        assert cond1 or cond2

        # Assign data.
        self.orderer = orderer
        self.planet_to_upgrade = planet
        self.upgrade_type = up_type
        self.new_colony_name = name
        self._phase = 1

    def execute(self, galaxy):
        # Preconditions.
        assert self.planet_to_upgrade in galaxy

        # See if the planet is at capacity
        maximum = 0
        current = 0
        if self.upgrade_type == ORDER_UPGRADE_SPACE_TYPE:
            maximum = self.planet_to_upgrade.max_space_colonies()
            current = len(self.planet_to_upgrade.space_colonies)
        elif self.upgrade_type == ORDER_UPGRADE_GROUND_TYPE:
            maximum = self.planet_to_upgrade.max_ground_colonies()
            current = len(self.planet_to_upgrade.ground_colonies)

        # Is the planet at capacity?
        if current == maximum:
            return ORDER_FAILED

        # Create the new colony.
        import colony as colony_lib
        colony = colony_lib.Colony(self.new_colony_name)
        if self.upgrade_type == ORDER_UPGRADE_SPACE_TYPE:
            self.planet_to_upgrade.space_colonies.append(colony)
        elif self.upgrade_type == ORDER_UPGRADE_GROUND_TYPE:
            self.planet_to_upgrade.ground_colonies.append(colony)

        # Colony added. We're done here.
        galaxy.update()
        return ORDER_NEXT_TURN



def upgrade_planet_order_from_dict(data, game, user):
    """
    Args:
        data (dict):
        game (Game): The current `Game`.
        user (User): The `User` who sent the order.

    Returns:
        An `UpgradePlanetOrder`
    """

    player = game.player_for_user(user)
    galaxy = game.galaxy

    planet_to_upgrade_unique = int(data['planet_to_upgrade'])
    upgrade_type = int(data['upgrade_type'])
    name = data['new_colony_name']

    planet_to_upgrade = galaxy.planet_for_unique(planet_to_upgrade_unique)

    # Return the UpgradePlanetOrder
    return UpgradePlanetOrder(player, planet_to_upgrade, upgrade_type, name)



class BuildFleetOrder(Order):
    at_planet = None
    in_fleet = 0
    ships = 0

    def __init__(self, orderer, at_planet, in_fleet, ships):
        """
        Args:
            orderer (Player):
            at_planet (Planet):
            in_fleet (int):
            ships (int): The number of ships to build.
        """

        # Preconditions
        assert orderer is not None
        assert at_planet is not None
        assert ships >= 1
        assert 0 <= in_fleet <= 2
        assert at_planet.owner == orderer

        # Assign data.
        self.orderer = orderer
        self.at_planet = at_planet
        self.in_fleet = in_fleet
        self.ships = ships

    def execute(self, galaxy):
        # Preconditions
        assert self.at_planet in galaxy
        assert 0 <= self.in_fleet <= 2

        if self._phase != 3:
            self._phase += 1
            return ORDER_NOT_FINISHED
        else:
            # See if we have enough money to build the fleet
            cost = self.at_planet.starship_build_cost(self.ships)
            if cost > self.orderer.money:
                return ORDER_FAILED
            else:
                self.orderer.money -= cost
                self.at_planet.fleets[self.in_fleet] += ships
                db.session.commit()
                return ORDER_NEXT_TURN



def build_fleet_order_from_dict(data, game, user):
    """
    Args:
        data (dict):
        game (Game):
        user (User):

    Returns:
        A `BuildFleetOrder`
    """

    player = game.player_for_user(user)
    galaxy = game.galaxy

    at_planet_unique = int(data['at_planet'])
    in_fleet = int(data['in_fleet'])
    ships = int(data['ships'])

    at_planet = galaxy.planet_for_unique(at_planet_unique)

    # Return the BuildFleetOrder
    return BuildFleetOrder(player, at_planet, in_fleet, ships)



def process_orders(user, game, move=[], hyperspace=[], build_ships=[],
                   upgrade_planet=[]):
    """
    Args:
        user (User):
        game (Game):

    Keyword Args:
        move
        hyperspace
        build_ships
        upgrade_planet
    """

    # Ensure that the provided user can access this game.
    assert game.has_user(user)



@app.route('/game/getorders', methods=['POST'])
def web_get_orders():
    # Get the current user.
    from interstellarage import current_user
    user = current_user()
    if user is None:
        return "Not logged in", 400

    # Get the game from the input.
    game_id = int(request.form['game'])
    game = game_lib.find(unique=game_id)
    if game is None:
        return "No game with that ID exists", 400
    elif user not in game:
        return "You are not in this game", 400

    # TODO
    pass
