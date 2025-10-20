
import psycopg2

class PostgresConnectorContextManager:
    def __init__(self, db_host: str, db_name: str, ...):
        # init

    def __enter__(self):
        # create conn

    def __exit__(self, exc_type, exc_value, exc_tb):
        # close conn

    def get_data_sql(self, sql):
        # exec query, result = pandas df


