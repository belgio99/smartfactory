from typing import Optional, List
from pydantic import BaseModel

class KpiRequest(BaseModel):
    """
    KpiRequest is a model representing a request to calculate a KPI (Key Performance Indicator).

    Attributes:
        KPI_Name (str): The name of the KPI to be calculated.
        Machine_Name (Optional[str]): The name of the machine for which the KPI is to be calculated. Default is None.
        Machine_Type (Optional[str]): The type of the machine for which the KPI is to be calculated. Default is None.
        Date_Start (Optional[str]): The start date for the KPI calculation period. Default is None.
        Date_End (Optional[str]): The end date for the KPI calculation period. Default is None.
        Aggregator (Optional[str]): The aggregator function to be used for the KPI calculation. Default is None.
        startPreviousPeriod (Optional[str]): The start date for the previous period to compare against. Default is None.
        endPreviousPeriod (Optional[str]): The end date for the previous period to compare against. Default is None.

    Methods:
        to_dict() -> dict:
            Converts the KpiRequest instance to a dictionary, excluding attributes that are None.
    """
    KPI_Name: str
    Machine_Name: Optional[str] = None
    Machine_Type: Optional[str] = None
    Date_Start: Optional[str] = None
    Date_End: Optional[str] = None
    Aggregator: Optional[str] = None
    startPreviousPeriod: Optional[str] = None
    endPreviousPeriod: Optional[str] = None

    def to_dict(self):
        return {key: value for key, value in {
            "KPI_Name": self.KPI_Name,
            "Machine_Name": self.Machine_Name,
            "Machine_Type": self.Machine_Type,
            "Date_Start": self.Date_Start,
            "Date_End": self.Date_End,
            "Aggregator": self.Aggregator,
            "startPreviousPeriod": self.startPreviousPeriod,
            "endPreviousPeriod": self.endPreviousPeriod
        }.items() if value is not None}