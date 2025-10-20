import os
import pandas as pd

from data_dev.queries import (
    TRANSFORM_PATIENT_SUM_TREATMENT_COST_PER_FACILITY_TYPE_SQL,
    TRANSFORM_FACILITY_NAME_MIN_TIME_SPENT_PER_VISIT_DATE_SQL,
    TRANSFORM_FACILITY_TYPE_AVG_TIME_SPENT_PER_VISIT_DATE_SQL
)
from data_dev.config import parquet_storage_config


class LoadParquet:
    """
    A class to handle the transformation and loading of data into Parquet files.

    Attributes:
    -----------
    connection_object : object
        Database connection object used to execute SQL queries.
    storage_path_facility_type_avg_time_spent_per_visit_date : str
        Path to store the Parquet file for facility type average time spent per visit date.
    storage_path_patient_sum_treatment_cost_per_facility_type : str
        Path to store the Parquet file for patient sum treatment cost per facility type.
    storage_path_facility_name_min_time_spent_per_visit_date : str
        Path to store the Parquet file for facility name minimum time spent per visit date.

    Methods:
    --------
    read_data(query):
        Executes the given SQL query and returns the result as a DataFrame.
    to_parquet(df, storage_path, partition_columns):
        Writes the given DataFrame to a Parquet file at the specified storage path, partitioned by the given columns.
    transform_facility_type_avg_time_spent_per_visit_date():
        Transforms data for facility type average time spent per visit date and writes it to a Parquet file.
    transform_patient_sum_treatment_cost_per_facility_type():
        Transforms data for patient sum treatment cost per facility type and writes it to a Parquet file.
    transform_facility_name_min_time_spent_per_visit_date():
        Transforms data for facility name minimum time spent per visit date and writes it to a Parquet file.
    load_parquet():
        Executes all transformations and loads the results into Parquet files.
    """

    def __init__(self, connection_object):
        """
        Initializes the LoadParquet class with a database connection object and storage paths.

        Parameters:
        -----------
        connection_object : object
            Database connection object used to execute SQL queries.
        """
        self.connection_object = connection_object
        self.storage_path_facility_type_avg_time_spent_per_visit_date = (
            parquet_storage_config.storage_path_facility_type_avg_time_spent_per_visit_date
        )
        self.storage_path_patient_sum_treatment_cost_per_facility_type = (
            parquet_storage_config.storage_path_patient_sum_treatment_cost_per_facility_type
        )
        self.storage_path_facility_name_min_time_spent_per_visit_date = (
            parquet_storage_config.storage_path_facility_name_min_time_spent_per_visit_date
        )

    def read_data(self, query):
        """
        Executes the given SQL query and returns the result as a DataFrame.

        Parameters:
        -----------
        query : str
            SQL query to execute.

        Returns:
        --------
        DataFrame
            Resulting data from the SQL query.
        """
        df = self.connection_object.get_data_sql(query=query)
        return df

    @staticmethod
    def to_parquet(df, storage_path, partition_columns):
        """
        Writes the given DataFrame to a Parquet file at the specified storage path, partitioned by the given columns.

        Parameters:
        -----------
        df : DataFrame
            Data to write to the Parquet file.
        storage_path : str
            Path to store the Parquet file.
        partition_columns : list
            Columns to partition the Parquet file by.
        """
        os.makedirs(storage_path, exist_ok=True)
        df.to_parquet(
            storage_path,
            engine='pyarrow',
            partition_cols=partition_columns,
            index=False,
            existing_data_behavior='delete_matching'
        )

    def transform_facility_type_avg_time_spent_per_visit_date(self):
        """
        Transforms data for facility type average time spent per visit date and writes it to a Parquet file.
        """
        df = self.read_data(TRANSFORM_FACILITY_TYPE_AVG_TIME_SPENT_PER_VISIT_DATE_SQL)
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        df['partition_date'] = df['visit_date'].dt.to_period('M').astype(str)
        self.to_parquet(
            df=df,
            storage_path=self.storage_path_facility_type_avg_time_spent_per_visit_date,
            partition_columns=['partition_date']
        )

    # TODO: do better approach for: df['facility_type_partition'] = df['facility_type'] - workaround,
    def transform_patient_sum_treatment_cost_per_facility_type(self):
        """
        Transforms data for patient sum treatment cost per facility type and writes it to a Parquet file.
        """
        df = self.read_data(TRANSFORM_PATIENT_SUM_TREATMENT_COST_PER_FACILITY_TYPE_SQL)
        df['facility_type_partition'] = df['facility_type'].str.replace(" ", "_")
        self.to_parquet(
            df=df,
            storage_path=self.storage_path_patient_sum_treatment_cost_per_facility_type,
            partition_columns=['facility_type_partition']
        )

    def transform_facility_name_min_time_spent_per_visit_date(self):
        """
        Transforms data for facility name minimum time spent per visit date and writes it to a Parquet file.
        """
        df = self.read_data(TRANSFORM_FACILITY_NAME_MIN_TIME_SPENT_PER_VISIT_DATE_SQL)
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        df['partition_date'] = df['visit_date'].dt.to_period('M').astype(str)
        self.to_parquet(
            df=df,
            storage_path=self.storage_path_facility_name_min_time_spent_per_visit_date,
            partition_columns=['partition_date']
        )

    def load_parquet(self):
        """
        Executes all transformations and loads the results into Parquet files.
        """
        self.transform_facility_type_avg_time_spent_per_visit_date()
        self.transform_patient_sum_treatment_cost_per_facility_type()
        self.transform_facility_name_min_time_spent_per_visit_date()
