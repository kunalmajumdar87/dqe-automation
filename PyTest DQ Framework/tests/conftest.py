import os
from pathlib import Path

import pytest

from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.connectors.file_system.parquet_reader import ParquetReader
from src.data_quality.data_quality_validation_library import DataQualityLibrary


def _default_parquet_root() -> str:
    current_file = Path(__file__).resolve()
    framework_root = current_file.parents[1]
    repo_root = framework_root.parent
    return str(repo_root / "parquet_data")


def pytest_addoption(parser):
    parser.addoption("--db_host", action="store", default="localhost", help="Database host")
    parser.addoption("--db_port", action="store", default="5434", help="Database port")
    parser.addoption("--db_name", action="store", default="mydatabase", help="Database name")
    parser.addoption("--db_user", action="store", default=os.getenv("DB_USER", "myuser"), help="Database user")
    parser.addoption(
        "--db_password",
        action="store",
        default=os.getenv("DB_PASSWORD", "mypassword"),
        help="Database password",
    )
    parser.addoption(
        "--parquet_root",
        action="store",
        default=_default_parquet_root(),
        help="Root path where parquet_data folder exists",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "dq: Data quality tests")
    config.addinivalue_line("markers", "unit: Unit tests")


@pytest.fixture(scope="session")
def settings(request):
    return {
        "db_host": request.config.getoption("db_host"),
        "db_port": int(request.config.getoption("db_port")),
        "db_name": request.config.getoption("db_name"),
        "db_user": request.config.getoption("db_user"),
        "db_password": request.config.getoption("db_password"),
        "parquet_root": Path(request.config.getoption("parquet_root")).resolve(),
    }


@pytest.fixture(scope='session')
def db_connection(settings):
    try:
        with PostgresConnectorContextManager(
            db_host=settings["db_host"],
            db_port=settings["db_port"],
            db_name=settings["db_name"],
            db_user=settings["db_user"],
            db_password=settings["db_password"],
        ) as db_connector:
            yield db_connector
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnectorContextManager: {e}")


@pytest.fixture(scope="session")
def parquet_reader():
    return ParquetReader()


@pytest.fixture(scope="session")
def data_quality_library():
    return DataQualityLibrary()