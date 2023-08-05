import enum
from typing import Union

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class Location:
    lon: str
    lat: str
    name: str


@dataclass(frozen=True)
class ForecastParams:
    # Air params:
    TEMPERATURE = "temperature"

    # Wind params:
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    WIND_GUSTS = "wind_gusts"


class ForecastModels(enum.Enum):
    MODEL_ICON = "icon"
    DEFAULT = "default"


@dataclass
class WeatherData:
    data: pd.DataFrame


@dataclass
class Forecast(WeatherData):
    """
    Forecast domain model represents a forecast for a location for a given time interval.

    This object is part of the core domain of this project and will utilize various modules:
        1. Fetch the Forecast object with the ForecastService.
        2. Store Forecast object in repository.
        3. Apply domain logic to find the best forecast model for a given location.
    """

    created_at: datetime
    valid_at: datetime
    location: Location
    weather_model: ForecastModels
    id: Union[int, None] = None

    def set_id(self, identifier: int) -> None:
        if self.id:
            raise
        self.id = identifier

    def __eq__(self, other: object) -> bool:
        """
        data property is a DataFrame object that needs special treatment.
        TODO: This can be implemented smarter.
        """
        if not isinstance(other, Forecast):
            return NotImplemented

        return (
            self.id == other.id
            and self.created_at == other.created_at
            and self.valid_at == other.valid_at
            and all(self.data == other.data)
            and self.location == other.location
        )
