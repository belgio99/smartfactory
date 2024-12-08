from pydantic import BaseModel

class Kpi(BaseModel):
    """
    Kpi class represents a Key Performance Indicator (KPI) model.

    Attributes:
        id (str): Unique identifier for the KPI.
        description (str): Description of the KPI.
        formula (str): Formula used to calculate the KPI.
        unit_measure (str): Unit of measurement for the KPI.
        forecastable (bool): Indicates if the KPI is forecastable.
        atomic (bool): Indicates if the KPI is atomic.

    Methods:
        to_dict(): Converts the Kpi instance to a dictionary.
    """
    id: str
    description: str
    formula: str
    unit_measure: str
    forecastable: bool
    atomic: bool

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "formula": self.formula,
            "unit_measure": self.unit_measure,
            "forecastable": self.forecastable,
            "atomic": self.atomic
        }