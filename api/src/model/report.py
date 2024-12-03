from pydantic import BaseModel

class Report(BaseModel):
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
    data: str