from kpi_dataframe_filter import kpi_dataframe_filter
from kpi_data_extraction import kpi_dataframe_data_extraction
import pandas as pd
import requests, os
from sympy import symbols, parse_expr

class kpi_engine:
    def energy_cost_savings(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd_current = df
        fd_previous = df

        cost_previous = kpi_dataframe_data_extraction.sum_kpi(df=fd_previous, machine_type=machine_type, kpi='cost', machine_id=machine_id, start_period=start_previous_period, end_period=end_previous_period)
        cost_current = kpi_dataframe_data_extraction.sum_kpi(df=fd_current, machine_type=machine_type, kpi='cost', machine_id=machine_id, start_period=start_period, end_period=end_period)

        return cost_previous - cost_current

    def energy_cost_working_time(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        total_energy_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_working', machine_id='all_machines', start_period=start_period, end_period=end_period)
        total_working_time = kpi_dataframe_filter.filter_dataframe_by_time(df=fd, machine_type=machine_type, start_period=start_period, end_period=end_period)['time'].nunique() * 24
        return  total_energy_cost / total_working_time

    def energy_cost_idle_time(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        total_energy_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_idle', machine_id='all_machines', start_period=start_period, end_period=end_period)
        total_working_time = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='working_time', machine_id='all_machines', start_period=start_period, end_period=end_period)
        return  total_energy_cost / total_working_time

    def energy_cost_per_unit(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        total_working_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_working', machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_idle_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_idle', machine_id=machine_id, start_period=start_period, end_period=end_period)
        return total_working_cost + total_idle_cost

    def power_consumption_efficiency(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        total_working_time = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_power_consumption = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='consumption', machine_id=machine_id, start_period=start_period, end_period=end_period)
        return total_working_time / total_power_consumption
        
    def power_consumption_trend(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        current_total_power_consumption = kpi_dataframe_data_extraction.sum_kpi(df=fd, kpi='consumption', machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        previous_total_power_consumption = kpi_dataframe_data_extraction.sum_kpi(df=fd, kpi='consumption', machine_type=machine_type, machine_id=machine_id, start_period=start_previous_period, end_period=end_previous_period)
        return (current_total_power_consumption - previous_total_power_consumption) / previous_total_power_consumption

    def machine_utilization_rate(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        total_working_time = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', machine_type=machine_type, df=fd, machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_idle_time = kpi_dataframe_data_extraction.sum_kpi(kpi='idle_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_offline_time = kpi_dataframe_data_extraction.sum_kpi(kpi='offline_time', machine_type=machine_type, df=fd, machine_id=machine_id, start_period=start_period, end_period=end_period)
        return total_working_time / (total_working_time + total_idle_time + total_offline_time)

    '''
    def machine_usage_trend(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        if(not(start_previous_period <= end_previous_period < start_period <= end_period)):
            print("bad chronological order")
        current_average_working_time = kpi_dataframe_data_extraction.avg_kpi(df=fd, machine_type=machine_type, kpi='working_time', machine_id=machine_id, start_period=start_period, end_period=end_period)
        previous_average_working_time = kpi_dataframe_data_extraction.avg_kpi(df=fd, machine_type=machine_type, kpi='working_time', machine_id=machine_id, start_period=start_previous_period, end_period=end_previous_period)
        return (current_average_working_time - previous_average_working_time) / previous_average_working_time
    '''

    '''
    def cost_per_unit():
        return -1, "-1"

    def material_cost_per_unit():
        return -1, "-1"

    def material_cost_per_unit():
        return -1, "-1"
    '''

    def availability(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        uptime = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        downtime = kpi_dataframe_data_extraction.sum_kpi(kpi='idle_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        return uptime / (uptime + downtime)

    def performance(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        total_output = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        total_productive_time = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        return total_output / total_productive_time

    def throughput(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        items_produced = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        time_employed = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period) + kpi_dataframe_data_extraction.sum_kpi(kpi='idle_time', df=fd, machine_id=machine_id, start_period=start_period, end_period=end_period)
        return items_produced / time_employed

    def quality(df, machine_id, machine_type, start_period, end_period, start_previous_period, end_previous_period):
        fd = df
        good_work = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        bad_work = kpi_dataframe_data_extraction.sum_kpi(kpi='bad_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        total_work = good_work + bad_work
        return good_work / total_work

    def yield_fft(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        fd = df
        defective_output = kpi_dataframe_data_extraction.sum_kpi(kpi='bad_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        total_output = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period) + defective_output
        return (total_output - defective_output) / total_output

    '''
    def maintenance_cost():
        return -1, "-1"

    def mean_time_between_failures():
        return -1, "-1"

    def mean_time_between_maintenance():
        return -1, "-1"

    def mean_time_to_repair():
        return -1, "-1"
    '''

    def dynamic_kpi(df, machine_id, machine_type, start_period, end_period, kpi_id):
        fd = df

        # kpi_formula = extract formula through API and kpi_id
        # response = requests.get(f"{os.getenv('BASE_URL')}/kb/retrieve/{kpi_id}")
        # formula = response.get("atomic_formula")
        # unit_of_measure = response.get("unit_measure")
        formula = '((cycles_sum - bad_cycles_sum) / cycles_sum) * (working_time_sum / (working_time_sum + idle_time_sum))'
        unit_of_measure = '%'
        expr = parse_expr(formula)

        # data extraction and symbol substitution
        substitutions = {}
        for symbol in expr.free_symbols:
            data_extraction_method = getattr(kpi_dataframe_data_extraction, str(symbol)[-3:]+"_kpi")
            substitutions[symbol] = data_extraction_method(df=df, kpi=str(symbol)[:-4], machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)

        result = expr.subs(substitutions)

        # formula evaluation
        eval_result = result.evalf()
        return float(eval_result), unit_of_measure