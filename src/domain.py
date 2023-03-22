import abc

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


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
class ForecastParams(BaseDomainModel):
    # Air params
    TEMPERATURE = "temperature"

    # Wind params
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    WIND_GUSTS = "wind_gusts"


@dataclass(frozen=True)
class Forecast(BaseDomainModel):
    """Forecast domain model represents a forecast for a location for a given time interval."""
    #: A timestamp when the forecast was created.
    created_at: datetime
    #: A timestamp when the forecast is valid.
    valid_at: datetime
    #: Pandas DataFrame containing forecast data.
    data: pd.DataFrame

