from pydantic import BaseModel
from storage.storage_operations import insert_model_to_storage
from typing import List
from typing import Optional
from enum import Enum

class Json_in_el(BaseModel):
    """
    Prediction input

    Machine_name and KPI_name (str): identifiers of the KPI to be predicted
    Date_prediction: number of days to forecast
    """
    Machine_name: str
    KPI_name: str
    Date_prediction: int

class Json_in(BaseModel):
    value: List[Json_in_el]

class LimeExplainationItem(BaseModel):
    date_info: str
    value: float

class Json_out_el(BaseModel):
    """
    The output of a prediction

    Machine_name (str) and KPI_name are the identifiers for the predicted series
    Predicted_value (List[flaot]): the list of the results
    Lower_bound, Upper_bound & confidence_score (List[float]): 
        each prediction has a "confidence_score chance to fall between "Lower_bound" and "Upper_bound"
    Lime_explaination (List[float]): explaination of which components influenced more the answer
    Measure_unit (str) the KPI's unit of measure
    Date_prediction (list[str]) date of the corresponding prediction
    Error_message (str): in case of error its description will be here
    Forecast (bool): forecast identifier
    """
    Machine_name: str
    KPI_name: str
    Predicted_value: Optional[List[float]]
    Lower_bound: List[float]
    Upper_bound: List[float]
    Confidence_score: List[float]
    Lime_explaination: List[List[LimeExplainationItem]]
    Measure_unit: str
    Date_prediction: List[str]
    Error_message: str
    Forecast: bool

class Json_out(BaseModel):
    value: List[Json_out_el]

class Severity(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Alert(BaseModel):
    """
    Represents an alert in the system.

    Attributes:
        alertId (str): Unique identifier for the alert.
        title (str): Title of the alert.
        type (str): Type of the alert.
        description (str): Detailed description of the alert.
        triggeredAt (str): Timestamp when the alert was triggered.
        isPush (bool): Indicates if the alert should be sent as a push notification.
        isEmail (bool): Indicates if the alert should be sent as an email.
        recipients (List[str]): List of recipients for the alert notifications.
        severity (Severity): Severity level of the alert.

    Methods:
        to_dict(): Converts the Alert instance to a dictionary.
    """
    alertId: Optional[int] = None
    title: str
    type: str
    description: str
    triggeredAt: str
    machineName: str
    isPush: bool
    isEmail: bool
    recipients: List[str]
    severity: Severity
    def to_dict(self):
        return {
            "alertId": self.alertId,
            "title": self.title,
            "type": self.type,
            "description": self.description,
            "triggeredAt": self.triggeredAt,
            "machineName": self.machineName,
            "isPush": self.isPush,
            "isEmail": self.isEmail,
            "recipients": self.recipients,
            "severity": self.severity.value
        }