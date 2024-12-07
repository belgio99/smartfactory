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
        group_by (str): The group by value.
        group_time: optional (str): The time interval for grouping.
        group_category: optional (str): The category for grouping.
        aggregations: {
            operation (str): The operation to perform, ex "SUM".
            field (str): The field to perform the operation on.
            }
    """
    aggregations: dict
    kpi: str
    timeframe: dict
    machines: list
    group_time: Optional[str] = None
    

class HistoricalData(BaseModel):
    data: dict
