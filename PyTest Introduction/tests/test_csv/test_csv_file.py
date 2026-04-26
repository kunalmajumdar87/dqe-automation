import pytest
import re


CSV_SCHEMA = ["id", "name", "age", "email", "is_active"]
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def test_file_not_empty(csv_df):
    assert not csv_df.empty


@pytest.mark.validate_csv
def test_validate_schema(csv_df, schema_validator):
    assert schema_validator(actual_schema=csv_df.columns, expected_schema=CSV_SCHEMA)


@pytest.mark.validate_csv
@pytest.mark.skip(reason="Age validation temporarily skipped as requested.")
def test_age_column_valid(csv_df):
    assert csv_df["age"].between(0, 100, inclusive="both").all()


@pytest.mark.validate_csv
def test_email_column_valid(csv_df):
    assert csv_df["email"].astype(str).apply(lambda email: bool(EMAIL_REGEX.match(email))).all()


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="Known issue: duplicate rows exist in source data.")
def test_duplicates(csv_df):
    assert not csv_df.duplicated().any()


@pytest.mark.parametrize(
    "player_id, expected_is_active",
    [
        (1, False),
        (2, True),
    ],
)
def test_active_players(csv_df, player_id, expected_is_active):
    actual_value = csv_df.loc[csv_df["id"] == player_id, "is_active"].iloc[0]
    assert actual_value == expected_is_active


def test_active_player_id_2(csv_df):
    actual_value = csv_df.loc[csv_df["id"] == 2, "is_active"].iloc[0]
    assert actual_value is True
