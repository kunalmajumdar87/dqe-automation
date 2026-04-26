import pytest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV_PATH = BASE_DIR / "src" / "data" / "data.csv"


@pytest.fixture(scope="session")
def csv_content():
	"""Return a callable that reads CSV content from the provided path."""

	def _read_csv(path_to_file):
		return pd.read_csv(path_to_file)

	return _read_csv


@pytest.fixture(scope="session")
def schema_validator():
	"""Return a callable that validates the actual schema against expected schema."""

	def _validate_schema(actual_schema, expected_schema):
		return list(actual_schema) == list(expected_schema)

	return _validate_schema


@pytest.fixture(scope="session")
def csv_df(csv_content):
	"""Shared dataframe loaded from the default CSV path."""
	return csv_content(DEFAULT_CSV_PATH)


def pytest_collection_modifyitems(items):
	"""Assign a custom mark to tests that do not declare any explicit mark."""
	for item in items:
		if not item.own_markers:
			item.add_marker(pytest.mark.unmarked)
