from pydantic import BaseModel
from typing import List
from typing import Optional

class Json_in_el(BaseModel):
    Machine_name: str
    KPI_name: str
    Date_prediction: int

class Json_in(BaseModel):
    value: List[Json_in_el]

class Json_out_el(BaseModel):
    Machine_name: str
    KPI_name: str
    Predicted_value: Optional[List[float]]
    Lower_bound: List[float]
    Upper_bound: List[float]
    Confidence_score: List[float]
    Lime_explaination: List[float]
    Measure_unit: str
    Date_prediction: List[str]
    Forecast: bool

class Json_out(BaseModel):
    value: List[Json_out_el]
