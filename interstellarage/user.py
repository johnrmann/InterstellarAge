"""
InterstellarAge
"""

# The User class will be a subclass of DatabaseRecord, enabling TODO
from database import DatabaseRecord, DATABASE_NAME

# Define global variables
USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 32

class User(DatabaseRecord):
    """
    TODO

    Public Attributes:
        username (str): TODO
        password_hash (str): The hashed version of this `User`'s password.
        email (str): The `User`'s e-mail address.

    Inherited Attributes:
        unique (int): TODO
    """

    username = ""
    password_hash = ""
    email = ""

    current_games = []

    def __init__(self, username, password_hash, email):
        """
        Validates and assigns data.

        Precondition:
            The password before becomming `password_hash` was checked for
            length.
        """

        global USERNAME_MIN_LENGTH
        global USERNAME_MAX_LENGTH

        # Validate username input -- check length and ensure that nobody else
        # has chosen this username.
        assert USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH
        # TODO nobody else has chosen this username.

        # Validate email input -- check length and ensure that it matches the
        # regular expression for an email address
        # TODO

        # Assign data
        self.username = username
        self.password_hash = password_hash
        self.email = email

        # Record this new user in the SQL database
        super(User,self).__init__("users", DATABASE_NAME)



def find(unique=None, username=None, email=None):
    """
    Finds a user and returns their `User` object.

    Args:
        unique (int): The `User`'s unique ID given to it during the initial SQL
            insert query.
        username (str):
        email (str):

    Returns:
        The `User` object if it was found. If it wasn't found, then `None` is
        returned.
    """

    if unique == None and username == None and email == None:
        return None

    # Find with unique
    elif unique != None:
        pass

    # Find with username
    elif username != None:
        pass

    # Find with email
    elif email != None:
        pass
