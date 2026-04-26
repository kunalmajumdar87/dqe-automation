import pytest


EXPECTED_SQL = """
SELECT
    f.facility_type,
    CONCAT(p.first_name, ' ', p.last_name) AS full_name,
    SUM(v.treatment_cost) AS sum_treatment_cost
FROM visits v
JOIN facilities f
    ON f.id = v.facility_id
JOIN patients p
    ON p.id = v.patient_id
GROUP BY
    f.facility_type,
    full_name
"""


@pytest.fixture(scope="module")
def expected_source_df(db_connection):
    return db_connection.get_data_sql(EXPECTED_SQL)


@pytest.fixture(scope="module")
def actual_parquet_df(settings, parquet_reader):
    parquet_path = settings["parquet_root"] / "patient_sum_treatment_cost_per_facility_type"
    return parquet_reader.read_dataset(parquet_path)


@pytest.mark.dq
def test_patient_sum_dataset_not_empty(actual_parquet_df, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(
        df=actual_parquet_df,
        dataset_name="patient_sum_treatment_cost_per_facility_type",
    )


@pytest.mark.dq
def test_patient_sum_not_null_names(actual_parquet_df, data_quality_library):
    data_quality_library.check_not_null_values(
        df=actual_parquet_df,
        column_names=["full_name"],
        dataset_name="patient_sum_treatment_cost_per_facility_type",
    )


@pytest.mark.dq
def test_patient_sum_non_negative_cost(actual_parquet_df, data_quality_library):
    data_quality_library.check_non_negative_values(
        df=actual_parquet_df,
        column_name="sum_treatment_cost",
        dataset_name="patient_sum_treatment_cost_per_facility_type",
    )


@pytest.mark.dq
def test_patient_sum_data_matches_source(expected_source_df, actual_parquet_df, data_quality_library):
    data_quality_library.check_data_full_data_set(
        expected_df=expected_source_df,
        actual_df=actual_parquet_df,
        sort_by=["facility_type", "full_name"],
        numeric_columns=["sum_treatment_cost"],
        dataset_name="patient_sum_treatment_cost_per_facility_type",
    )
