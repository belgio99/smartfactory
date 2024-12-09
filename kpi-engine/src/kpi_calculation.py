from kpi_dataframe_filter import kpi_dataframe_filter
from kpi_data_extraction import kpi_dataframe_data_extraction
import pandas as pd
import requests, os
from sympy import symbols, parse_expr

class kpi_engine:
    def energy_cost_savings(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the energy cost savings for a specific machinery by comparing the total energy costs 
        of a previous period with those of the current period.

        Parameters:
        df (DataFrame): The input dataframe containing energy cost data with a 'cost' column.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation will include all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            will include all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for comparison, formatted as a string.
        end_period (str): The end of the current time period for comparison, formatted as a string.

        Returns:
        float: The energy cost savings calculated as:
            energy_cost_savings = cost_sum_previous - cost_sum_current

           Where:
           - cost_sum_previous is the sum of costs for the previous period.
           - cost_sum_current is the sum of costs for the current period.
        """
        fd_current = df
        fd_previous = df

        cost_previous = kpi_dataframe_data_extraction.sum_kpi(df=fd_previous, machine_type=machine_type, kpi='cost', machine_id=machine_id, start_period=start_previous_period, end_period=end_previous_period)
        cost_current = kpi_dataframe_data_extraction.sum_kpi(df=fd_current, machine_type=machine_type, kpi='cost', machine_id=machine_id, start_period=start_period, end_period=end_period)

        return cost_previous - cost_current, "€/kWh"


    def energy_cost_working_time(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
            """
            Calculates the energy cost per unit of working time for the specified period, providing 
            a normalized view of energy utilization efficiency during active operation.

            Parameters:
            df (DataFrame): The input dataframe containing energy cost and working time data.
            machine_id (str): The identifier of the machine for filtering. In this implementation, 
                            all machines are included by default as 'all_machines'.
            machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                                will include all machine types.
            start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
            end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
            start_period (str): The start of the current time period for analysis, formatted as a string.
            end_period (str): The end of the current time period for analysis, formatted as a string.

            Returns:
            float: The normalized energy cost per unit of working time, calculated as:
                energy_cost_working_time = total_energy_cost / total_working_time

                Where:
                - total_energy_cost is the sum of energy costs for the current period, extracted from 
                    the 'cost_working' KPI.
                - total_working_time is the total number of unique working hours in the period, 
                    calculated as the number of unique time entries in the filtered dataframe multiplied by 24 (hours/day).
            """
            fd = df
            total_energy_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_working', machine_id='all_machines', start_period=start_period, end_period=end_period)
            total_working_time = kpi_dataframe_filter.filter_dataframe_by_time(df=fd, machine_type=machine_type, start_period=start_period, end_period=end_period)['time'].nunique() * 24
            return  total_energy_cost / total_working_time, "€/kWh"

    def energy_cost_idle_time(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the energy cost per unit of idle time for the specified period, providing a 
        normalized measure of energy waste during non-operational periods.

        Parameters:
        df (DataFrame): The input dataframe containing energy cost and working time data.
        machine_id (str): The identifier of the machine for filtering. In this implementation, 
                        all machines are included by default as 'all_machines'.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            will include all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The normalized energy cost per unit of idle time, calculated as:
            energy_cost_idle_time = total_energy_cost / total_working_time

            Where:
            - total_energy_cost is the sum of energy costs incurred during idle periods, extracted from 
                the 'cost_idle' KPI.
            - total_working_time is the total working time in the period, calculated using the 
                'working_time' KPI.
        """
        fd = df
        total_energy_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_idle', machine_id='all_machines', start_period=start_period, end_period=end_period)
        total_working_time = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='working_time', machine_id='all_machines', start_period=start_period, end_period=end_period)
        return  total_energy_cost / total_working_time, "€/kWh"

    def energy_cost_per_unit(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Computes the total energy cost for a single unit over a specified period of time. 
        This KPI combines both working and idle energy costs to provide a comprehensive 
        measure of the total energy expenditure for the unit.

        Parameters:
        df (DataFrame): The input dataframe containing energy cost data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation will include all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            will include all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The total energy cost for the unit, calculated as:
            energy_cost_per_unit = total_working_cost + total_idle_cost
            Where:
            - total_working_cost is the energy cost incurred during active operation.
            - total_idle_cost is the energy cost incurred during idle periods.
        """
        fd = df
        total_working_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_working', machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_idle_cost = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='cost_idle', machine_id=machine_id, start_period=start_period, end_period=end_period)
        return total_working_cost + total_idle_cost, "€/kWh"

    def power_consumption_efficiency(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the energy efficiency of a specific machine over a given time interval. 
        This KPI provides insight into how effectively a machine converts consumed power into 
        productive working time.

        Parameters:
        df (DataFrame): The input dataframe containing power consumption and working time data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The energy efficiency of the machine, calculated as:
            power_consumption_efficiency = total_working_time / total_power_consumption

            Where:
            - total_working_time is the sum of working time over the specified period, derived from 
                the `working_time` KPI.
            - total_power_consumption is the total power consumed during the same period, derived 
                from the `consumption` KPI.
        """
        fd = df
        total_working_time = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_power_consumption = kpi_dataframe_data_extraction.sum_kpi(df=fd, machine_type=machine_type, kpi='consumption', machine_id=machine_id, start_period=start_period, end_period=end_period)
        return total_working_time / total_power_consumption, "%"
        
    def power_consumption_trend(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the percentage change in a machine's energy consumption between two time periods. 
        A positive value indicates an increase in energy consumption, while a negative value suggests 
        a decrease. This KPI helps track the trend of energy usage over time.

        Parameters:
        df (DataFrame): The input dataframe containing power consumption data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The percentage change in energy consumption, calculated as:
            power_consumption_trend = (current_total_power_consumption - previous_total_power_consumption) / previous_total_power_consumption

            Where:
            - current_total_power_consumption is the total power consumed in the current period, derived 
                from the `consumption` KPI.
            - previous_total_power_consumption is the total power consumed in the previous period, also 
                derived from the `consumption` KPI.
        """
        fd = df
        current_total_power_consumption = kpi_dataframe_data_extraction.sum_kpi(df=fd, kpi='consumption', machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        previous_total_power_consumption = kpi_dataframe_data_extraction.sum_kpi(df=fd, kpi='consumption', machine_type=machine_type, machine_id=machine_id, start_period=start_previous_period, end_period=end_previous_period)
        return (current_total_power_consumption - previous_total_power_consumption) / previous_total_power_consumption, "%"

    def machine_utilization_rate(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the utilization rate of a machine over a specified period. 
        This KPI measures the proportion of time the machine was actively working compared to 
        the total available time, including working, idle, and offline periods.

        Parameters:
        df (DataFrame): The input dataframe containing machine usage data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The machine utilization rate, calculated as:
            machine_utilization_rate = total_working_time / (total_working_time + total_idle_time + total_offline_time)

            Where:
            - total_working_time is the total time the machine was actively working.
            - total_idle_time is the total time the machine was idle, not in use.
            - total_offline_time is the total time the machine was offline, unable to operate.
        """
        fd = df
        total_working_time = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', machine_type=machine_type, df=fd, machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_idle_time = kpi_dataframe_data_extraction.sum_kpi(kpi='idle_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        total_offline_time = kpi_dataframe_data_extraction.sum_kpi(kpi='offline_time', machine_type=machine_type, df=fd, machine_id=machine_id, start_period=start_period, end_period=end_period)
        return total_working_time / (total_working_time + total_idle_time + total_offline_time), "%"

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
        """
        Calculates the availability of a machine during a specified time period. 
        This KPI measures the percentage of time the machine was in operation (uptime) 
        compared to the total available time, including both uptime and downtime.

        Parameters:
        df (DataFrame): The input dataframe containing machine usage data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The availability percentage, calculated as:
            availability = uptime / (uptime + downtime)

            Where:
            - uptime is the total time the machine was operational and working.
            - downtime is the total time the machine was idle and unavailable for operation.
        """
        fd = df
        uptime = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        downtime = kpi_dataframe_data_extraction.sum_kpi(kpi='idle_time', df=fd, machine_type=machine_type, machine_id=machine_id, start_period=start_period, end_period=end_period)
        return uptime / (uptime + downtime), "%"

    def performance(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the performance of a machine during a specified time period. 
        This KPI measures the percentage of actual output (good cycles) produced compared to the total productive time 
        available for the machine, providing an efficiency metric for the machine's operation.

        Parameters:
        df (DataFrame): The input dataframe containing machine usage and output data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The performance percentage, calculated as:
            performance = total_output / total_productive_time

            Where:
            - total_output is the total number of good cycles (actual output) produced by the machine during the period.
            - total_productive_time is the total time the machine was working (productive time) during the period.
        """
        fd = df
        total_output = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        total_productive_time = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        return total_output / total_productive_time, "%"

    def throughput(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Calculates the throughput of a machine during a specified time period. 
        This KPI measures the average number of items produced per unit of total time employed 
        (including both working time and idle time) during the period, offering insights into the overall efficiency 
        of the production process.

        Parameters:
        df (DataFrame): The input dataframe containing machine usage and output data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.

        Returns:
        float: The throughput, calculated as:
            throughput = items_produced / time_employed

            Where:
            - items_produced is the total number of good cycles (finished items) produced by the machine during the period.
            - time_employed is the total time the machine was employed, including both working time and idle time.
        """
        fd = df
        items_produced = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        time_employed = kpi_dataframe_data_extraction.sum_kpi(kpi='working_time', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period) + kpi_dataframe_data_extraction.sum_kpi(kpi='idle_time', df=fd, machine_id=machine_id, start_period=start_period, end_period=end_period)
        return items_produced / time_employed, "items/s"

    def quality(df, machine_id, machine_type, start_period, end_period, start_previous_period, end_previous_period):
        """
        Calculates the quality of the production process for a specific machine during a given time period.
        This KPI measures the percentage of correctly produced pieces (good cycles) compared to the total 
        number of pieces produced (good cycles + bad cycles), providing insights into the effectiveness of the production process.

        Parameters:
        df (DataFrame): The input dataframe containing machine usage and production data.
        machine_id (str): The identifier of the machine for filtering. If 'all_machines' is provided, 
                        the calculation includes all machines.
        machine_type (str): The type of machine for filtering. If 'any' is provided, the calculation 
                            includes all machine types.
        start_period (str): The start of the current time period for analysis, formatted as a string.
        end_period (str): The end of the current time period for analysis, formatted as a string.
        start_previous_period (str): The start of the previous time period for comparison, formatted as a string.
        end_previous_period (str): The end of the previous time period for comparison, formatted as a string.

        Returns:
        float: The quality KPI, calculated as:
            quality = good_work / total_work

            Where:
            - good_work is the total number of good cycles (correctly produced pieces).
            - total_work is the sum of good cycles and bad cycles (total number of pieces produced).
        """
        fd = df
        good_work = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        bad_work = kpi_dataframe_data_extraction.sum_kpi(kpi='bad_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        total_work = good_work + bad_work
        return good_work / total_work, "%"

    def yield_fft(df, machine_id, machine_type, start_previous_period, end_previous_period, start_period, end_period):
        """
        Measures the First Time Through (FTT) or Yield indicator, which quantifies the proportion of output correctly produced 
        without defects on the first pass relative to the total output in a specified time period.

        Parameters:
        - df: DataFrame containing the relevant KPI data.
        - machine_id: Identifier for the specific machine to analyze.
        - machine_type: Type of the machine to filter the data.
        - start_previous_period: Start date of the previous period for comparison (not used in the formula but included for consistency).
        - end_previous_period: End date of the previous period for comparison (not used in the formula but included for consistency).
        - start_period: Start date of the period for which the Yield indicator is calculated.
        - end_period: End date of the period for which the Yield indicator is calculated.

        Returns:
        - A tuple containing:
        - The yield as a decimal (fraction of correctly produced output relative to total output).
        - A string indicating the unit ("%").
        """
        fd = df
        defective_output = kpi_dataframe_data_extraction.sum_kpi(kpi='bad_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period)
        total_output = kpi_dataframe_data_extraction.sum_kpi(kpi='good_cycles', df=fd, machine_id=machine_id, machine_type=machine_type, start_period=start_period, end_period=end_period) + defective_output
        return (total_output - defective_output) / total_output, "%"

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
        headers = {
            "x-api-key": "b3ebe1bb-a4e7-41a3-bbcc-6c281136e234",
            "Content-Type": "application/json"
        }
        response = requests.get(f"http://kb:8000/kb/{kpi_id}/get_kpi", headers=headers)
        response = response.json()
        print(response)
        if response.get("atomic") == True:
            formula = response.get("id")
        else:
            formula = response.get("atomic_formula")
        unit_of_measure = response.get("unit_measure")
        # formula = 'cycles_max'
        # unit_of_measure = '%'
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