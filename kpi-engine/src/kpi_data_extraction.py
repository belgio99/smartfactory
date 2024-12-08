from kpi_dataframe_filter import kpi_dataframe_filter
import pandas as pd

class kpi_dataframe_data_extraction:
    """
    A class containing methods to compute statistical metrics (sum, average, max, min, 
    standard deviation, median) for Key Performance Indicators (KPIs) from a filtered dataframe.
    Each method utilizes the filtering functionality provided by the `kpi_dataframe_filter` module.
    """

    def sum_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Computes the sum of KPI values in the 'sum' column for the filtered dataframe.

        Parameters:
        kpi (str): The name of the KPI to analyze.
        df (DataFrame): The input dataframe containing KPI data.
        machine_id (str): The identifier of the machine for filtering.
        machine_type (str): The type of machine for filtering.
        start_period (str): The start of the time period for filtering.
        end_period (str): The end of the time period for filtering.

        Returns:
        float: The total sum of values in the 'sum' column for the filtered dataframe.
        """
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].sum()

    def avg_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Computes the average KPI value from the 'avg' column for the filtered dataframe.

        Parameters:
        kpi (str): The name of the KPI to analyze.
        df (DataFrame): The input dataframe containing KPI data.
        machine_id (str): The identifier of the machine for filtering.
        machine_type (str): The type of machine for filtering.
        start_period (str): The start of the time period for filtering.
        end_period (str): The end of the time period for filtering.

        Returns:
        float: The average value in the 'avg' column for the filtered dataframe.
        """
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['avg'].sum() / fd.shape[0]

    def max_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Finds the maximum KPI value from the 'sum' column for the filtered dataframe.

        Parameters:
        kpi (str): The name of the KPI to analyze.
        df (DataFrame): The input dataframe containing KPI data.
        machine_id (str): The identifier of the machine for filtering.
        machine_type (str): The type of machine for filtering.
        start_period (str): The start of the time period for filtering.
        end_period (str): The end of the time period for filtering.

        Returns:
        float: The maximum value in the 'sum' column for the filtered dataframe.
        """
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].max()

    def min_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Finds the minimum KPI value from the 'sum' column for the filtered dataframe.

        Parameters:
        kpi (str): The name of the KPI to analyze.
        df (DataFrame): The input dataframe containing KPI data.
        machine_id (str): The identifier of the machine for filtering.
        machine_type (str): The type of machine for filtering.
        start_period (str): The start of the time period for filtering.
        end_period (str): The end of the time period for filtering.

        Returns:
        float: The minimum value in the 'sum' column for the filtered dataframe.
        """
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].min()

    def std_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Computes the standard deviation of KPI values from the 'sum' column for the filtered dataframe.

        Parameters:
        kpi (str): The name of the KPI to analyze.
        df (DataFrame): The input dataframe containing KPI data.
        machine_id (str): The identifier of the machine for filtering.
        machine_type (str): The type of machine for filtering.
        start_period (str): The start of the time period for filtering.
        end_period (str): The end of the time period for filtering.

        Returns:
        float: The standard deviation of values in the 'sum' column for the filtered dataframe.
        """
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].std()

    def med_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Computes the median of KPI values from the 'sum' column for the filtered dataframe.

        Parameters:
        kpi (str): The name of the KPI to analyze.
        df (DataFrame): The input dataframe containing KPI data.
        machine_id (str): The identifier of the machine for filtering.
        machine_type (str): The type of machine for filtering.
        start_period (str): The start of the time period for filtering.
        end_period (str): The end of the time period for filtering.

        Returns:
        float: The median of values in the 'sum' column for the filtered dataframe.
        """
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].median()