from data_dev.queries import (CREATE_FACILITIES_TABLE_QUERY,
                              CREATE_PATIENTS_TABLE_QUERY,
                              CREATE_VISITS_TABLE_QUERY)
from data_dev.queries import (MERGE_PATIENTS_QUERY,
                              MERGE_VISITS_QUERY,
                              MERGE_FACILITIES_QUERY)
from data_dev.config import load_config


class NF3Loader:
    """
    A class to handle the loading and transformation of data into a 3NF (Third Normal Form) database schema.

    This class is responsible for:
    1. Creating the necessary database tables if they do not already exist.
    2. Merging data into the 3NF tables using predefined SQL queries.

    Attributes:
        conn: A psycopg2 database connection object used to interact with the database.
    """

    def __init__(self, conn):
        """
        Initialize the NF3Loader with a database connection.

        Args:
            conn: A psycopg2 database connection object.
        """
        self.conn = conn

    def load_data(self):
        """
        Load and transform data into the 3NF database schema.

        This method performs the following steps:
        1. Creates the necessary tables (facilities, patients, visits) if they do not already exist.
        2. Merges data into the 3NF tables using predefined SQL queries.
        3. Commits the transaction if all operations succeed.
        4. Rolls back the transaction and prints the error if any operation fails.

        Raises:
            Exception: If any SQL execution fails, the exception is caught, the transaction is rolled back,
                       and the error is printed.
        """
        cursor = self.conn.cursor()
        try:
            # Create tables if they do not exist
            cursor.execute(CREATE_FACILITIES_TABLE_QUERY)
            cursor.execute(CREATE_PATIENTS_TABLE_QUERY)
            cursor.execute(CREATE_VISITS_TABLE_QUERY)

            # Merge data into 3NF tables
            cursor.execute(MERGE_FACILITIES_QUERY)
            cursor.execute(MERGE_PATIENTS_QUERY)
            cursor.execute(MERGE_VISITS_QUERY, {'date_scope': load_config.date_scope})

            # Commit the transaction
            self.conn.commit()
        except Exception as e:
            # Rollback the transaction in case of an error
            self.conn.rollback()
            print(f"An error occurred during data loading: {e}")
        finally:
            # Close the cursor
            cursor.close()
