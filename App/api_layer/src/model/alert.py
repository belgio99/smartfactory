from pydantic import BaseModel
from typing import List

class Alert(BaseModel):
    """
    Represents an alert notification with various delivery methods.

    Attributes:
        notificationTitle (str): The title of the notification.
        notificationText (str): The text content of the notification.
        isPush (bool): Indicates if the notification should be sent as a push notification.
        isEmail (bool): Indicates if the notification should be sent as an email.
        recipients (List[str]): A list of recipients who will receive the notification.
    """
    notificationTitle: str
    notificationText: str
    isPush: bool
    isEmail: bool
    recipients: List[str]