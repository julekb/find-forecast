import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Union

import pandas as pd


@dataclass(frozen=True)
class Location:
    lon: str
    lat: str
    name: str


class WeatherParams(str, enum.Enum):
    # Meta:
    TIMESTAMP = "timestamp"

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
    TYPE_IDENTIFIER = "historical"

    data: pd.DataFrame

    location: Location

    def __add__(self, other):
        if not isinstance(other, WeatherData):
            raise TypeError("Incorrect types.")

        if self.location != other.location:
            raise Exception

        if self.TYPE_IDENTIFIER != other.TYPE_IDENTIFIER:
            self.data["type"] = self.TYPE_IDENTIFIER
            other.data["type"] = other.TYPE_IDENTIFIER

            self.data.set_index(["type"], append=True, inplace=True)
            other.data.set_index(["type"], append=True, inplace=True)

        self.data = pd.concat([self.data, other.data])

        return self


@dataclass
class Forecast(WeatherData):
    """
    Weather data container.

    This object is part of the core domain of this project and will utilize various modules:
        1. Fetch the Forecast object with the ForecastService.
        2. Store Forecast object in repository.
        3. Apply domain logic to find the best forecast model for a given location.
    """

    TYPE_IDENTIFIER = "forecast"

    created_at: datetime
    valid_at: datetime
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
