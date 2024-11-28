import pandas as pd

class kpi_dataframe_filter:
    def filter_dataframe_by_machine(df, machine_id):
        if machine_id != 'all_machines':
            return df[df['asset_id'] == machine_id]
        return df
    
    def filter_dataframe_by_typology(df,machine_type): 
        if machine_type != 'any':
            return df[df['name'].str.startswith(machine_type)]
        return df
    
    def filter_dataframe_by_kpi(df, kpi):
        return df[df['kpi'] == kpi]

    def filter_dataframe_by_time(df, start_period, end_period):
        if start_period > end_period:
            raise ValueError("Error: start_time cannot come after end_time.")
        return df[(df['time'] >= start_period) & (df['time'] <= end_period)]

    def filter_df(kpi, df, machine_id, machine_type, start_period, end_period):
        fd = df #fd  = filtered dataframe
        fd = kpi_dataframe_filter.filter_dataframe_by_machine(fd, machine_id)
        fd = kpi_dataframe_filter.filter_dataframe_by_typology(fd, machine_type)
        fd = kpi_dataframe_filter.filter_dataframe_by_kpi(fd, kpi)
        fd = kpi_dataframe_filter.filter_dataframe_by_time(fd, start_period, end_period)
        return fd