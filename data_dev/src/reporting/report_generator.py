import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os

from data_dev.config import report_generator_config


class ReportGenerator:
    """
    A class to generate an HTML report with a table and a doughnut chart visualizing
    last week's data and the minimum average time spent by facility type.

    Attributes:
        data (pd.DataFrame): The source data loaded from a Parquet files.
        fig (plotly.graph_objects.Figure): A combined figure containing a table and a doughnut chart.

    Methods:
        combine_figures(): Initializes the combined figure layout with a table and doughnut chart.
        read_source_data(): Reads the source data from a Parquet file.
        transform_data(): Filters and sorts the data for the last week.
        create_table_element(last_week_data): Adds a table visualization to the figure.
        create_doughnut_element(last_week_data): Adds a doughnut chart visualization to the figure.
        update_layout(): Updates the layout of the combined figure.
        write_html(): Writes the generated figure to an HTML file.
        generate_report(): Main method to generate the report.
    """

    def __init__(self):
        """
        Initializes the ReportGenerator instance by loading the data and setting up the figure.
        """
        self.data = self.read_source_data()
        self.fig = self.combine_figures()

    @staticmethod
    def combine_figures():
        """
        Creates a combined figure layout with a table and a doughnut chart.

        Returns:
            plotly.graph_objects.Figure: A figure with two subplots - a table and a doughnut chart.
        """
        return make_subplots(
            rows=2, cols=1,
            specs=[[{"type": "table"}], [{"type": "domain"}]],
            subplot_titles=("Last week loaded data", "Min average time spent by Facility Type for the last week")
        )

    @staticmethod
    def read_source_data():
        """
        Reads the source data from a Parquet file specified in the configuration.

        Returns:
            pd.DataFrame: The loaded data.
        """
        return pd.read_parquet(report_generator_config.parquet_files_path)

    def transform_data(self):
        """
        Filters the data for the last week and sorts it by visit date and facility type.

        Returns:
            pd.DataFrame: The transformed data for the last week.
        """
        self.data['visit_date'] = pd.to_datetime(self.data['visit_date'])
        last_loaded_date = self.data['visit_date'].max()
        last_week_data = self.data[self.data['visit_date'] >= (last_loaded_date - pd.Timedelta(days=6))]
        last_week_data = last_week_data.sort_values(by=['visit_date', 'facility_type'], ascending=False)
        return last_week_data

    def create_table_element(self, last_week_data):
        """
        Adds a table visualization to the figure.

        Args:
            last_week_data (pd.DataFrame): The data for the last week to be visualized.
        """
        self.fig.add_trace(
            go.Table(
                header=dict(
                    values=["Facility Type", "Visit Date", "Average Time Spent"],
                    fill_color="lightgrey",
                    align="center",
                    font=dict(size=12, color="black"),
                ),
                cells=dict(
                    values=[
                        last_week_data["facility_type"],
                        last_week_data["visit_date"].dt.strftime('%Y-%m-%d'),  # Format dates as strings
                        last_week_data["avg_time_spent"]
                    ],
                    fill_color="white",
                    align="center",
                    font=dict(size=12, color="black"),
                ),
            ),
            row=1, col=1
        )

    def create_doughnut_element(self, last_week_data):
        """
        Adds a doughnut chart visualization to the figure.

        Args:
            last_week_data (pd.DataFrame): The data for the last week to be visualized.
        """
        doughnut_data = last_week_data.groupby('facility_type')['avg_time_spent'].min()
        self.fig.add_trace(
            go.Pie(
                labels=doughnut_data.index,
                values=doughnut_data.values,
                hole=0.5,
                textinfo='label+value',  # Show actual values instead of percentages
                textfont=dict(size=14)  # Adjust font size for better readability
            ),
            row=2, col=1
        )

    def update_layout(self):
        """
        Updates the layout of the combined figure, including height and title.
        """
        self.fig.update_layout(
            height=800,
            title_text='DQE Automation - "BI" HTML Report with Table and Doughnut Chart',
            title_x=0.5
        )

    def write_html(self):
        """
        Writes the generated figure to an HTML file in the specified storage path.

        The file is named "report.html".
        """
        os.makedirs(report_generator_config.storage_path, exist_ok=True)
        pio.write_html(self.fig, file=os.path.join(report_generator_config.storage_path, "report.html"),
                       auto_open=False)

    def generate_report(self):
        """
        Main method to generate the HTML report.

        This method:
        - Transforms the source data to filter the last week's data.
        - Creates a table and doughnut chart elements.
        - Updates the layout of the figure.
        - Writes the figure to an HTML file.
        """
        last_week_data = self.transform_data()
        self.create_table_element(last_week_data)
        self.create_doughnut_element(last_week_data)
        self.update_layout()
        self.write_html()
