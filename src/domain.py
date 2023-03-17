from typing import List, Dict
import abc

from dataclasses import dataclass, InitVar, field
from datetime import datetime


class BaseDomainModel(abc.ABC):
    """Abstract base domain class."""


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
    #: A timestamp when the forecast was created.
    created_at: datetime
    #: A timestamp when the forecast is valid.
    valid_at: datetime

    data: List[Dict[datetime, ConditionsDataPoint]]

