import pandas as pd


class DataQualityLibrary:
    """Reusable assertion helpers for validating pandas DataFrames."""

    NULL_TOKEN = "<NULL>"

    @classmethod
    def _normalize_for_compare(cls, df: pd.DataFrame, numeric_columns: list[str] | None = None) -> pd.DataFrame:
        normalized_df = df.copy()
        numeric_columns = numeric_columns or []

        for col in normalized_df.columns:
            if col in numeric_columns:
                normalized_df[col] = pd.to_numeric(normalized_df[col], errors="coerce").round(2)
            else:
                normalized_df[col] = normalized_df[col].astype(str).replace("NaT", cls.NULL_TOKEN)
                normalized_df[col] = normalized_df[col].replace("None", cls.NULL_TOKEN)
                normalized_df[col] = normalized_df[col].replace("nan", cls.NULL_TOKEN)

        return normalized_df

    @staticmethod
    def check_duplicates(df: pd.DataFrame, column_names: list[str] | None = None, dataset_name: str = "dataset"):
        subset = column_names if column_names else None
        duplicates_mask = df.duplicated(subset=subset)
        duplicate_count = int(duplicates_mask.sum())
        assert duplicate_count == 0, f"{dataset_name} contains {duplicate_count} duplicate row(s)."

    @staticmethod
    def check_count(df1: pd.DataFrame, df2: pd.DataFrame, df1_name: str = "source", df2_name: str = "target"):
        assert len(df1) == len(df2), (
            f"Row count mismatch: {df1_name}={len(df1)} rows, {df2_name}={len(df2)} rows."
        )

    def check_data_full_data_set(
        self,
        expected_df: pd.DataFrame,
        actual_df: pd.DataFrame,
        sort_by: list[str],
        numeric_columns: list[str] | None = None,
        dataset_name: str = "dataset",
    ):
        expected_df = expected_df.copy()
        actual_df = actual_df.copy()

        expected_columns = list(expected_df.columns)
        actual_columns = list(actual_df.columns)
        missing_columns = [col for col in expected_columns if col not in actual_columns]
        assert not missing_columns, (
            f"Column mismatch for {dataset_name}. Missing columns in actual dataset: {missing_columns}."
        )
        actual_df = actual_df[expected_columns]

        expected_norm = self._normalize_for_compare(expected_df, numeric_columns=numeric_columns)
        actual_norm = self._normalize_for_compare(actual_df, numeric_columns=numeric_columns)

        expected_norm = expected_norm.sort_values(by=sort_by).reset_index(drop=True)
        actual_norm = actual_norm.sort_values(by=sort_by).reset_index(drop=True)

        if not expected_norm.equals(actual_norm):
            merged = expected_norm.merge(actual_norm, how="outer", indicator=True)
            diff_sample = merged[merged["_merge"] != "both"].head(10).to_dict(orient="records")
            raise AssertionError(
                f"Data mismatch detected for {dataset_name}. Sample differences: {diff_sample}"
            )

    @staticmethod
    def check_dataset_is_not_empty(df: pd.DataFrame, dataset_name: str = "dataset"):
        assert not df.empty, f"{dataset_name} is empty."

    @staticmethod
    def check_not_null_values(df: pd.DataFrame, column_names: list[str], dataset_name: str = "dataset"):
        null_counts = {col: int(df[col].isna().sum()) for col in column_names}
        columns_with_nulls = {col: count for col, count in null_counts.items() if count > 0}
        assert not columns_with_nulls, f"{dataset_name} has NULLs in columns: {columns_with_nulls}"

    @staticmethod
    def check_non_negative_values(df: pd.DataFrame, column_name: str, dataset_name: str = "dataset"):
        negative_count = int((pd.to_numeric(df[column_name], errors="coerce") < 0).sum())
        assert negative_count == 0, f"{dataset_name} has {negative_count} negative values in {column_name}."
