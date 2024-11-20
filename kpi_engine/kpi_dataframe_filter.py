import padas as pd

class kpi_dataframe_filter:
    def filter_dataframe_by_machine(df, machine_id):
        if machine_id != 'all_machines':
            return df[df['asset_id'] == machine_id]
        return df

    def filter_dataframe_by_kpi(df, kpi):
        return df[df['kpi'] == kpi]

    def filter_dataframe_by_time(df, start_time, end_time):
        if start_time > end_time:
            return -1
        return df[(df['time'] >= start_time) & (df['time'] <= end_time)]