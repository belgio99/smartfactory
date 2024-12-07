from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

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