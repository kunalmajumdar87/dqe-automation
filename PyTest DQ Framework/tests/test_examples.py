import pandas as pd
import pytest


@pytest.mark.unit
def test_check_dataset_is_not_empty(data_quality_library):
    data_quality_library.check_dataset_is_not_empty(pd.DataFrame({"id": [1]}), dataset_name="unit_df")


@pytest.mark.unit
def test_check_duplicates_detects_duplicates(data_quality_library):
    df = pd.DataFrame({"id": [1, 1]})
    with pytest.raises(AssertionError):
        data_quality_library.check_duplicates(df=df, column_names=["id"], dataset_name="dup_df")


@pytest.mark.unit
def test_check_non_negative_values_detects_negative(data_quality_library):
    df = pd.DataFrame({"sum_treatment_cost": [10, -5]})
    with pytest.raises(AssertionError):
        data_quality_library.check_non_negative_values(
            df=df,
            column_name="sum_treatment_cost",
            dataset_name="cost_df",
        )
