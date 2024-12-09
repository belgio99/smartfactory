from pydantic import BaseModel
from typing import Optional
class HistoricalQueryParams(BaseModel):
    """
    Represents the parameters that describe a query to retrieve historical data.

    Attributes:
        kpi (str): The key performance indicator.
        timeframe (dict): {
            start_date (str): The start date of the timeframe.
            end_date (str): The end date of the timeframe.
        }.
        machines (list(str)): machines of which the data is collected.
        group_time: optional (str): The time interval for grouping.
    """

    kpi: str
    timeframe: dict
    machines: list
    group_time: Optional[str] = None
    
