from typing import Optional
from pydantic import BaseModel
from model.task import SchedulingFrequency

class ReportResponse(BaseModel):
    """
    Represents a report.

    Attributes:
        id (str): The id of the report.
        type (str): The type of the report.
        name (str): The name of the report.
        data (str): The content of the report.
    """
    id: int
    name: str
    type: str

class ScheduledReport(BaseModel):
    id: Optional[int]
    name: str
    recurrence: SchedulingFrequency
    status: bool
    email: str
    startDate: str
    kpis: list
    machines: list

class Report(BaseModel):
    name: str
    type: str
    period: str
    status: bool
    email: str
    kpis: list
    machines: list