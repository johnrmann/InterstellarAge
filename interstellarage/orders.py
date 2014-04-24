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
    orderer = None



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
    """

    to_planet = None
    from_planet = None
    fleet_number = -1

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

    def execute(self, galaxy):
        """
        Returns:
            A tuple in the format `(int, MoveResult or None)`.

            The first item in the tuple is a code representing the general
            outcome of the order. For example, if the order is still
            incomplete, then the first item of the tuple will be
            `ORDER_NOT_FINISHED`.

            If the order is finished (`ORDER_NEXT_TURN`), then the second
            item of the tuple will be a `MoveOrder` object detailing the
            outcome of the move. This object will be returned as a `dict` to
            all players. This is to the clientside can update the game board.
        """

        # Declare global variables.
        global ORDER_NOT_FINISHED
        global ORDER_NEXT_TURN

        # Ensure data structure invaraints.
        assert self.from_planet in galaxy
        assert self.to_planet in galaxy

        # PHASE 1: Colonies built
        if self._phase == 1:
            self._phase = 2
            return (ORDER_NOT_FINISHED, None)

        # PHASE 2: Fleets leave their planet.
        if self._phase == 2:
            fleet_size = self.from_planet.fleet_departs(self.fleet_number)
            assert fleet_size > 0
            self._fleet_size = fleet_size
            self._phase = 3
            return (ORDER_NOT_FINISHED, None)

        # PHASE 3: Fleets are built
        if self._phase == 3:
            self._phase = 4
            return (ORDER_NOT_FINISHED, None)

        # PHASE 4: Fleets arrive at destination. They do combat if required.
        elif self._phase == 4:
            self.to_planet.receive_fleet(self._fleet_size, self.orderer)
            result = MoveResult(self)
            return (ORDER_NEXT_TURN, result)



class MoveResult(Result):
    def __init__(self, move_order):
        pass



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
            return (ORDER_NOT_FINISHED, None)

        # PHASE 2: Fleets depart planets
        if self._phase == 2:
            from_system = self.from_planet.system()

            fleet_size = self.from_planet.fleet_departs(self.fleet_number)
            assert fleet_size > 0
            self._fleet_size = fleet_size

            eta = from_system.hyperspace_distance(self.to_system, fleet_size)
            self._eta = eta
            self._phase = 3
            return (ORDER_NOT_FINISHED, None)

        # PHASE 3: Fleets are built
        if self._phase == 3:
            self._phase = 4
            return (ORDER_NOT_FINISHED, None)

        # PHASE 4: Fleets arrive at intrasystem destinations
        elif self._phase == 4:
            self._phase = 5
            return (ORDER_NOT_FINISHED_NEXT_TURN, None)

        # PHASE 5: Hyperspace travel
        elif self._phase == 5:
            self._eta -= 1
            if self._eta == 0:
                result = None # TODO
                if self.to_planet is not None:
                    self.to_planet.receive_fleet(self._fleet_size, self.orderer)
                else:
                    self.to_system.receive_fleet(self._fleet_size, self.orderer)
                return (ORDER_NEXT_TURN, result)
            else:
                return (ORDER_NOT_FINISHED_NEXT_TURN, None)



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
            return (ORDER_FAILED, None)

        # Create the new colony.
        import colony as colony_lib
        colony = colony_lib.Colony(self.new_colony_name)
        if self.upgrade_type == ORDER_UPGRADE_SPACE_TYPE:
            self.planet_to_upgrade.space_colonies.append(colony)
        elif self.upgrade_type == ORDER_UPGRADE_GROUND_TYPE:
            self.planet_to_upgrade.ground_colonies.append(colony)

        # Colony added. We're done here.
        galaxy.update()
        result = None # TODO
        return (ORDER_NEXT_TURN, result)



class BuildFleetOrder(Order):
    at_planet = None
    in_fleet = 0
    ships = 0

    def __init__(self, orderer, at_planet, in_fleet, ships):
        """
        Args:
            orderer (Playet):
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
            return (ORDER_NOT_FINISHED, None)
        else:
            # See if we have enough money to build the fleet
            cost = self.at_planet.starship_build_cost(self.ships)
            if cost > self.orderer.money:
                return (ORDER_FAILED, None)
            else:
                self.orderer.money -= cost
                self.at_planet.fleets[self.in_fleet] += ships
                db.session.commit()
                result = None
                return (ORDER_NEXT_TURN, result)



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
