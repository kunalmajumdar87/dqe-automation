from data_dev.src.data.data_generator import DataGenerator
from data_dev.queries import (
    CREATE_SRC_GENERATED_FACILITIES_TABLE_QUERY,
    CREATE_SRC_GENERATED_PATIENTS_TABLE_QUERY,
    CREATE_SRC_GENERATED_VISITS_TABLE_QUERY,
    INSERT_SRC_GENERATED_FACILITIES_QUERY,
    INSERT_SRC_GENERATED_PATIENTS_QUERY,
    INSERT_SRC_GENERATED_VISITS_QUERY
)


class GeneratedDataLoader:
    """
    A class to handle the generation and loading of synthetic data into a database.

    Attributes:
        conn (object): A database connection object.
        dg (DataGenerator): An instance of the DataGenerator class for generating synthetic data.

    Methods:
        - is_table_empty(cursor, table_name): Checks if a given table is empty.
        - inject_data_into_table(cursor, data, query): Inserts data into a table using a specified query.
        - inject_data(): Creates tables (if not exist) and injects generated data into the database.
    """

    def __init__(self, conn):
        """
        Initializes the GeneratedDataLoader with a database connection.

        Args:
            conn (object): A database connection object.
        """
        self.conn = conn
        self.dg = DataGenerator()

    @staticmethod
    def is_table_empty(cursor, table_name):
        """
        Checks if a given table is empty.

        Args:
            cursor (object): A database cursor object.
            table_name (str): The name of the table to check.

        Returns:
            bool: True if the table is empty, False otherwise.
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchone()[0] == 0

    @staticmethod
    def inject_data_into_table(cursor, data, query):
        """
        Inserts data into a table using a specified query.

        Args:
            cursor (object): A database cursor object.
            data (list): A list of data to be inserted.
            query (str): The SQL query for inserting data.
        """
        for params in data:
            cursor.execute(query, params)

    def inject_data(self):
        """
        Creates tables (if they don't exist) and injects generated data into the database.

        This method:
        1. Creates the `src_generated_facilities`, `src_generated_patients`, and 
           `src_generated_visits` tables if they do not already exist.
        2. Checks if the `src_generated_visits` table is empty.
        3. If the table is empty, generates synthetic data for facilities, patients, and visits.
        4. Inserts the generated data into the respective tables.
        5. Commits the transaction if successful, or rolls back in case of an error.
        """
        cursor = self.conn.cursor()
        try:
            # Create tables if they do not exist
            cursor.execute(CREATE_SRC_GENERATED_FACILITIES_TABLE_QUERY)
            cursor.execute(CREATE_SRC_GENERATED_PATIENTS_TABLE_QUERY)
            cursor.execute(CREATE_SRC_GENERATED_VISITS_TABLE_QUERY)

            # Generate and insert data if the visits table is empty
            if self.is_table_empty(cursor=cursor, table_name='src_generated_visits'):
                self.dg.generate_data()
                self.inject_data_into_table(
                    cursor=cursor,
                    data=self.dg.get_facilities(),
                    query=INSERT_SRC_GENERATED_FACILITIES_QUERY
                )
                self.inject_data_into_table(
                    cursor=cursor,
                    data=self.dg.get_patients(),
                    query=INSERT_SRC_GENERATED_PATIENTS_QUERY
                )
                self.inject_data_into_table(
                    cursor=cursor,
                    data=self.dg.get_visits(),
                    query=INSERT_SRC_GENERATED_VISITS_QUERY
                )
                self.conn.commit()
        except Exception as e:
            # Rollback the transaction in case of an error
            self.conn.rollback()
            print(f"Error occurred: {e}")
        finally:
            # Close the cursor
            cursor.close()
