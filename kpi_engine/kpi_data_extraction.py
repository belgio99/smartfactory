from kpi_dataframe_filter import kpi_dataframe_filter
import pandas as pd

class kpi_dataframe_data_extraction:
    def sum_kpi(kpi, df, machine_id, start_time, end_time):
        fd = df     # fd = filtered dataframe
        fd = kpi_dataframe_filter.filter_dataframe_by_machine(fd, machine_id)
        fd = kpi_dataframe_filter.filter_dataframe_by_kpi(fd, kpi)
        fd = kpi_dataframe_filter.filter_dataframe_by_time(fd, start_time, end_time)
        '''
        if machine_id != 'all_machines': 
            print(f"KPI calculated as sum on machine {machine_id} ({fd.iloc[0, 2]}) by summing {kpi} from {start_time} to {end_time}. Result is {fd['sum'].sum()}.")
        else: 
            print(f"KPI calculated as sum on machine {machine_id} by summing {kpi} from {start_time} to {end_time}. Result is {fd['sum'].sum()}.")
        '''
            
        return fd['sum'].sum()


    def avg_kpi(kpi, df, machine_id, start_time, end_time):
        fd = df     # fd = filtered dataframe
        fd = kpi_dataframe_filter.filter_dataframe_by_machine(fd, machine_id)
        fd = kpi_dataframe_filter.filter_dataframe_by_kpi(fd, kpi)
        fd = kpi_dataframe_filter.filter_dataframe_by_time(fd, start_time, end_time)
        '''
        print(f"KPI calculated as average on machine {machine_id} ({fd.iloc[0, 2]}) by averaging {kpi}s from {start_time} to {end_time}. Result is {fd['avg'].sum()/fd.shape[0]}.")
        '''
        return fd['avg'].sum()/fd.shape[0]

    def max_kpi(kpi, df, machine_id, start_time, end_time):
        fd = df #fd  = filtered dataframe
        fd = kpi_dataframe_filter.filter_dataframe_by_machine(fd, machine_id)
        fd = kpi_dataframe_filter.filter_dataframe_by_kpi(fd, kpi)
        fd = kpi_dataframe_filter.filter_dataframe_by_time(fd, start_time, end_time)
        '''
        print(f"KPI calculated on machine {machine_id} ({fd.iloc[0, 2]}) as maximum {kpi}s from {start_time} to {end_time}. Result is {fd['sum'].max()}.")
        '''
        return fd['sum'].max()


    def min_kpi(kpi, df, machine_id, start_time, end_time):
        fd = df #fd  = filtered dataframe
        fd = kpi_dataframe_filter.filter_dataframe_by_machine(fd, machine_id)
        fd = kpi_dataframe_filter.filter_dataframe_by_kpi(fd, kpi)
        fd = kpi_dataframe_filter.filter_dataframe_by_time(fd, start_time, end_time)
        '''
        print(f"KPI calculated on machine {machine_id} ({fd.iloc[0, 2]}) as minimum {kpi}s from {start_time} to {end_time}. Result is {fd['sum'].min()}.")
        '''
        fd['sum'].min()