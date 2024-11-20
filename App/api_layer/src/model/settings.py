from pydantic import BaseModel
from typing import Optional

class DashboardSettings(BaseModel): # Mock class for the DashboardSettings model
    name: Optional[str] = None
    value: Optional[int] = None
