from robot.api.deco import keyword
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

class Helper:
    @keyword
    def read_html_table_to_df(self, table_html):
        soup = BeautifulSoup(table_html, 'html.parser')
        table = soup.find('table')
        if table is None:
            raise ValueError("No <table> found in the provided HTML.")
        df = pd.read_html(StringIO(str(table)))[0]
        return df

    @keyword
    def read_parquet_with_filter(self, parquet_folder, filter_date=None, date_column='visit_date'):
        df = pd.read_parquet(parquet_folder)
        if filter_date:
            if date_column not in df.columns:
                raise KeyError(f"Column '{date_column}' not found in Parquet data. Available columns: {df.columns}")
            df = df[df[date_column] == filter_date]
        return df

    @keyword
    def compare_dataframes(self, df1, df2):
        if df1.equals(df2):
            return True, None
        else:
            diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
            return False, diff