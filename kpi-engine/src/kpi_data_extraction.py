from kpi_dataframe_filter import kpi_dataframe_filter
import pandas as pd

class kpi_dataframe_data_extraction:
    def sum_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].sum()


    def avg_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['avg'].sum()/fd.shape[0]

    def max_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        return fd['sum'].max()


    def min_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        fd['sum'].min()


    def std_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        fd['sum'].std()


    def med_kpi(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = kpi_dataframe_filter.filter_df(kpi, df, machine_id, machine_type, start_period, end_period)
        fd['sum'].median()