"""
InterstellarAge
"""

# Import MySQL module
import MySQLdb

# Define global variables
DATABASE_NAME = ""

class DatabaseRecord(object):
    """
    The `DatabaseRecord` class is to be used as a superclass for objects that
    can be saved to a SQL database.

    Public Attributes:
        unique (int): This value uniquely identifies this object from the
            others in the SQL table where the object is stored. This attribute
            is read only.

    Private Attributes:
        _sql_database (str): The name of the databsae to store this in.
        _sql_table (str): The name of the table for
        _connection: The connection to the database.
    """

    _sql_database = ""
    _sql_table = ""

    _connection = None

    unique = None

    def __init__(self, table, database):
        """
        Preconditions:
            1) A SQL database named `database` alredy exists.
            2) A SQL table named `table` already exists.

        Args:
            table (str): The name of the SQL table where SQL records of objects
                of this class will be stored.
            database (str): The name of the SQL database where SQL records of
                objects of this class will be stored.
        """

        self._sql_database = database
        self._sql_table = table

        # Connect to the database
        self._connect()

        query = "INSERT INTO {0} {1} VALUES {2};"
        columns = []
        values = []

        for item in dir(self):
            # Check for private or builtin
            if item[0] == '_':
                continue
            else:
                columns.append(item)
                to_append = self._get_sql_value(item)
                if to_append == None:
                    continue
                values.append(to_append)

        # Create the list of column names for the query
        columns_str = "("
        for column_name in columns:
            columns_str += column_name
            columns_str += ","
        columns_str[-1] = ")"
        if len(columns_str) == 1:
            columns_str = "()"
        
        # Create the list of values for the query
        values_str = "("
        for value in values:
            values_str += value
            values_str += ","
        values_str[-1] = ")"
        if len(values_str) == 1:
            values_str = "()"

        # Finalize the query and execute it
        query = query.format(table, columns_str, values_str)
        self._query(query)

        # Get the unique ID of the last inserted table row
        self.unique = int(_self._connection.insert_id())

    def save(self):
        """
        Updates the MySQL database to the record with this object's unique id
        matches the Attributes of this object.
        """

        query = "UPDATE {0} SET {1} WHERE {2} LIMIT 1;"
        where = "id={0}".format(str(self.unique))
        set_str = ""
        to_set = []

        for item in dir(self):
            # Check for private or builtin
            if item[0] == '_':
                continue
            value = self._get_sql_value(item)
            value_pair = (item, value)
            to_set.append(value_pair)

        # vpair2str : (str * str or int or float) -> str
        #
        # TODO
        vpair2str = lambda (item,val) : "{0}={1}".format(item,val)

        # Create set_str
        for pair in to_set:
            set_str += vpair2str(pair)
            set_str += ", "
        set_str[-2] = " "

        # Finalize the query and execute it
        query = query.format(self._sql_table, set_str, where)
        self._query(query)

    def _connect(self):
        """
        Creates a connection to the MySQL database.
        """

        self._connection = MySQLdb.connect()

    def _query(self, sql):
        """
        Executes a SQL query.
        """

        cursor = self._connection.cursor()
        cursor.execute(sql)

    def _get_sql_value(self, item):
        """
        TODO.

        Returns:
            A `str` version of `self.item` or `None` if `self.item` cannot be
            stored in a SQL table.
        """

        value = getattr(self, item)
        if isinstance(value, DatabaseRecord):
            value = str(value.unique)
        elif isinstance(value, int) or isinstance(value, float):
            value = str(value)
        elif hasattr(value, '__call__') or isinstance(value, list):
            return None
        else:
            value = "'"+self._connection.escape_string(str(value))+"'"
        return value
