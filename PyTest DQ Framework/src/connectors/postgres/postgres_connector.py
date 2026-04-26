from typing import Any, Optional

import pandas as pd
import psycopg2
from psycopg2.extensions import connection


class PostgresConnectorContextManager:
    """Context manager for PostgreSQL connectivity and reads."""

    def __init__(
        self,
        db_host: str,
        db_name: str,
        db_user: str,
        db_password: str,
        db_port: int = 5432,
        autocommit: bool = False,
    ):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.autocommit = autocommit
        self.connection: Optional[connection] = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        self.connection.autocommit = self.autocommit
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.connection:
            self.connection.close()

    def get_data_sql(self, sql: str, params: Optional[dict[str, Any]] = None) -> pd.DataFrame:
        if not self.connection:
            raise RuntimeError("Database connection is not initialized.")
        return pd.read_sql_query(sql=sql, con=self.connection, params=params)


