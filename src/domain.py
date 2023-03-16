from typing import List, Dict

from dataclasses import dataclass
from datetime import datetime


class BaseDomainModel:
    pass


@dataclass(frozen=True)
class Location(BaseDomainModel):
    """Location domain model."""
    #: Location's longitude.
    lon: str
    #: Location's latitude.
    lat: str
    # Location's name.
    name: str


@dataclass(frozen=True)
class ConditionsDataPoint(BaseDomainModel):
    wind_speed: float


@dataclass(frozen=True)
class Forecast(BaseDomainModel):
    """Forecast domain model represents a forecast for a location for a given time interval."""
    #: Creation date.
    created_at: datetime.date
    #: A timestamp when the forecast is valid.
    valid_at: datetime.date

    data: List[Dict[datetime, ConditionsDataPoint]]

