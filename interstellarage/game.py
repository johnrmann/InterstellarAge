"""
InterstellarAge
"""

# Import python modules
from datetime import datetime

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy.orm import relationship

# Import the database from the main file
from interstellarage import db

# Import the user class
from user import User

# Define global variables
FACTION_CODE_ISCA = 0
FACTION_CODE_GALAXYCORP = 1
FACTION_CODE_FSR = 2
FACTION_CODE_PRIVATEER = 3
NUMBER_OF_FACTIONS = 4

class Game(db.Model):
	"""
	Attributes:
		unique (int): This `Game`'s unique identifier.
		started_when (datetime): The date and time the game was started.

		user_isca_id (int):
		user_fsr_id (int):
		user_galaxycorp_id (int):
		user_privateer_id (int):
	"""

	__tablename__ = 'game'

	unique = db.Column(Integer, primary_key=True)
	started_when = db.Column(db.DateTime)

	user_isca_id = db.Column(Integer, ForeignKey('user.unique'))
	user_fsr_id = db.Column(Integer, ForeignKey('user.unique'))
	user_galaxycorp_id = db.Column(Integer, ForeignKey('user.unique'))
	user_privateer_id = db.Column(Integer, ForeignKey('user.unique'))

	user_isca =
		relationship("User", backref=db.backref('games_as_isca'))
	user_fsr =
		relationship("User", backref=db.backref('games_as_fsr'))
	user_galaxycorp =
		relationship("User",backref=db.backref('games_as_galaxycorp'))
	user_privateer =
		relationship("User", backref=db.backref('games_as_privateer'))

	def __init__ (self, isca=None, fsr=None, galaxycorp=None, privateer=None):
		"""
		Args:
			isca (User):
			fsr (User):
			galaxycorp (User):
			privateer (User):
		"""

		if isca != None:
			self.user_isca = isca
			self.user_isca_id = isca.unique
		elif fsr != None:
			self.user_fsr = fsr
			self.user_fsr_id = fsr.unique
		elif galaxycorp != None:
			self.user_galaxycorp = galaxycorp
			self.user_galaxycorp_id = galaxycorp.unique
		elif privateer != None:
			self.user_privateer = privateer
			self.user_privateer_id = privateer.unique
		else:
			# TODO error
			pass

		self.started_when = datetime.now()

		# Save changes to the sql database
		db.session.add(self)
		db.session.commit()