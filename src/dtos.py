"""Data transfer objects library."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ForecastDTO:
    """The forecast DTO."""
    value: float

