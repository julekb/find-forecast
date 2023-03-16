from typing import List, Dict
import abc

from dataclasses import dataclass, InitVar, field
from datetime import datetime


class BaseDomainModel(abc.ABC):
    """Abstract base domain class."""
    created_at: datetime = field(init=False)

    def __post_init__(self):
        """Automatically set created_at timestamp."""
        self.created_at = datetime.now()


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
    #: A timestamp when the forecast is valid.
    valid_at: datetime

    data: List[Dict[datetime, ConditionsDataPoint]]

