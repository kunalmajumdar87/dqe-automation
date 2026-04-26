import pytest


EXPECTED_SQL = """
SELECT
    f.facility_type,
    v.visit_timestamp::date AS visit_date,
    ROUND(AVG(v.duration_minutes), 2) AS avg_time_spent
FROM visits v
JOIN facilities f
    ON f.id = v.facility_id
GROUP BY
    f.facility_type,
    visit_date
"""


@pytest.fixture(scope="module")
def expected_source_df(db_connection):
    return db_connection.get_data_sql(EXPECTED_SQL)


@pytest.fixture(scope="module")
def actual_parquet_df(settings, parquet_reader):
    parquet_path = settings["parquet_root"] / "facility_type_avg_time_spent_per_visit_date"
    return parquet_reader.read_dataset(parquet_path)


@pytest.mark.dq
def test_facility_type_avg_dataset_not_empty(actual_parquet_df, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(
        df=actual_parquet_df,
        dataset_name="facility_type_avg_time_spent_per_visit_date",
    )


@pytest.mark.dq
def test_facility_type_avg_row_count(expected_source_df, actual_parquet_df, data_quality_library):
    data_quality_library.check_count(
        df1=expected_source_df,
        df2=actual_parquet_df,
        df1_name="postgres_expected",
        df2_name="parquet_actual",
    )


@pytest.mark.dq
def test_facility_type_avg_includes_all_facility_types(actual_parquet_df):
    found = set(actual_parquet_df["facility_type"].dropna().unique())
    expected = {"Hospital", "Clinic", "Urgent Care", "Specialty Center"}
    assert expected.issubset(found), f"Missing facility types in parquet output: {expected - found}"


@pytest.mark.dq
def test_facility_type_avg_data_matches_source(expected_source_df, actual_parquet_df, data_quality_library):
    data_quality_library.check_data_full_data_set(
        expected_df=expected_source_df,
        actual_df=actual_parquet_df,
        sort_by=["facility_type", "visit_date"],
        numeric_columns=["avg_time_spent"],
        dataset_name="facility_type_avg_time_spent_per_visit_date",
    )
