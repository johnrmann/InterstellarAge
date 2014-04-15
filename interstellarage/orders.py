# Import python modules.
import json

# Import TODO
from interstellarage import app
from user import User
from galaxy import Galaxy
from system import System
from planet import Planet

# Define global variables
ORDER_NOT_FINISHED = 0
ORDER_NEXT_TURN = 1
ORDER_NOT_FINISHED_NEXT_TURN 2

class Order(object):
	orderer = None
	_phase = 0

	def execute(self, galaxy):
		pass



class MoveOrder(Order):
	"""
	Attributes:
		orderer (User): The `User` that issued the orders.
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

	def execute(self, galaxy):
		# Declare global variables.
		global ORDER_NOT_FINISHED
		global ORDER_NEXT_TURN

		# Ensure data structure invaraints.
		assert self.from_planet.owner == self.orderer
		assert 0 <= self.fleet_number <= 2

		# PHASE 0: Fleets leave their planet.
		if self._phase == 0:
			fleet_size = self.from_planet.fleet_departs(self.fleet_number)
			assert fleet_size > 0
			self._fleet_size = fleet_size
			self._phase = 1
			return ORDER_NOT_FINISHED

		# PHASE 1: Fleets arrive at destination. They do combat if required.
		elif self._phase == 1:
			self.to_planet.receive_fleet(self._fleet_size, self.orderer)
			return ORDER_NEXT_TURN



class HyperspaceOrder(Order):
	from_planet = None
	fleet_number = -1
	to_planet = None
	to_system = None

	_eta = -1

	def execute(self, galaxy):
		# Declare global variables.
		global ORDER_NOT_FINISHED
		global ORDER_NEXT_TURN
		global ORDER_NOT_FINISHED_NEXT_TURN

		# Ensure data structure invariants.
		assert self.from_planet.owner == self.orderer
		assert 0 <= self.fleet_number <= 2

		if self.to_system is None:
			assert self.to_planet is not None
			self.to_system = self.to_planet.system()

		# PHASE 0:
		if self._phase == 0:
			from_system = self.from_planet.system()

			fleet_size = self.from_planet.fleet_departs(self.fleet_number)
			assert fleet_size > 0
			self._fleet_size = fleet_size

			eta = from_system.hyperspace_distance(self.to_system, fleet_size)
			self._eta = eta
			self._phase = 1
			return ORDER_NOT_FINISHED

		# PHASE 1:
		elif self._phase == 1:
			self._eta -= 1
			if self._eta == 0:
				if self.to_planet is not None:
					self.to_planet.receive_fleet(self._fleet_size, self.orderer)
				else:
					self.to_system.receive_fleet(self._fleet_size, self.orderer)
				return ORDER_NEXT_TURN
			else:
				return ORDER_NOT_FINISHED_NEXT_TURN



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
