import pandas as pd

class kpi_dataframe_filter:
    
    def filter_dataframe_by_machine(df, machine_id):
        """
        Filters the input dataframe based on a specific machine identifier.

        Parameters:
        df (DataFrame): The input dataframe containing data with an 'asset_id' column.
        machine_id (str): The identifier of the machine to filter by. 
                        If 'all_machines' is passed, no filtering is applied, 
                        and the entire dataframe is returned.

        Returns:
        DataFrame: A filtered dataframe containing only rows where the 'asset_id' column 
                matches the specified machine_id. If 'all_machines' is passed, 
                the original dataframe is returned without any changes.
        """
        if machine_id != 'all_machines':
            return df[df['asset_id'] == machine_id]
        return df


    def filter_dataframe_by_typology(df,machine_type): 
        """
        Filters the input dataframe based on the machine type.

        Parameters:
        df (DataFrame): The input dataframe containing data with a 'name' column.
        machine_type (str): The type of machine to filter by. If a specific type is provided,
                            rows are filtered to include only those where the 'name' column 
                            starts with the specified machine_type. If 'any' is passed, 
                            no filtering is applied, and the entire dataframe is returned.

        Returns:
        DataFrame: A filtered dataframe containing only rows where the 'name' column starts 
                with the specified machine_type. If 'any' is passed, the original dataframe 
                is returned without any changes.
        """
        if machine_type != 'any':
            return df[df['name'].str.startswith(machine_type)]
        return df

    
    def filter_dataframe_by_kpi(df, kpi):
        """
        Filters the input dataframe to include only rows corresponding to a specific KPI.

        Parameters:
        df (DataFrame): The input dataframe containing data with a 'kpi' column.
        kpi (str): The name of the KPI to filter by. Only rows where the 'kpi' column 
                matches this value will be included in the filtered dataframe.

        Returns:
        DataFrame: A filtered dataframe containing only rows where the 'kpi' column 
                matches the specified KPI.
        """
        return df[df['kpi'] == kpi]


    def filter_dataframe_by_time(df, start_period, end_period):
        """
        Filters the input dataframe based on a specified time period.

        Parameters:
        df (DataFrame): The input dataframe containing data with a 'time' column.
        start_period (str): The start of the time period, formatted as a string.
        end_period (str): The end of the time period, formatted as a string.

        Returns:
        DataFrame: A filtered dataframe containing only rows where the 'time' column 
                falls within the specified time period, inclusive of both start and end.

        Raises:
        ValueError: If the start_period is strictly later than the end_period, an error is raised 
                    to prevent invalid filtering.

        Notes:
        - The 'time' column in the dataframe is assumed to be in a format compatible with 
        string comparison or datetime operations.
        """
        if start_period > end_period:
            return ValueError("Error: start_time cannot come after end_time.")

        return df[(df['time'] >= start_period) & (df['time'] <= end_period)]


    def filter_df(kpi, df, machine_id, machine_type, start_period, end_period):
        """
        Applies a series of filtering operations to the input dataframe based on KPI, 
        machine ID, machine type, and time period.

        Parameters:
        kpi (str): The name of the KPI to filter by.
        df (DataFrame): The input dataframe containing the data to be filtered.
        machine_id (str): The identifier of the machine for filtering; can be specific or 
                        'all_machines' to include all machines.
        machine_type (str): The type of machine for filtering; can be specific or 'any' for all types.
        start_period (str): The start of the time period for filtering, formatted as a string.
        end_period (str): The end of the time period for filtering, formatted as a string.

        Returns:
        DataFrame: A dataframe filtered sequentially by:
                - Machine ID
                - Machine type
                - KPI
                - Time period (inclusive of start and end)
        
        Notes:
        - This method orchestrates calls to other filtering methods in the 
        `kpi_dataframe_filter` module, chaining their results to progressively refine 
        the dataset.
        - If no filters are applied (e.g., 'all_machines' and 'any' are passed, and no KPI or time filters 
        are specified), the original dataframe is returned.

        Example:
        The method performs the following operations in sequence:
        1. Filters by machine ID using `filter_dataframe_by_machine`.
        2. Filters by machine type using `filter_dataframe_by_typology`.
        3. Filters by KPI using `filter_dataframe_by_kpi`.
        4. Filters by time period using `filter_dataframe_by_time`.
        """
        fd = df #fd  = filtered dataframe
        fd = kpi_dataframe_filter.filter_dataframe_by_machine(fd, machine_id)
        fd = kpi_dataframe_filter.filter_dataframe_by_typology(fd, machine_type)
        fd = kpi_dataframe_filter.filter_dataframe_by_kpi(fd, kpi)
        fd = kpi_dataframe_filter.filter_dataframe_by_time(fd, start_period, end_period)
        if fd.empty: 
            return ValueError("Error: filter values are too restricted: no items are retrived")
        return fd