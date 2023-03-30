import abc
import enum
from typing import Union

from dataclasses import dataclass, field
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
    """
    Forecast params used to fetch a requested forecast.
    """
    # Air params:
    TEMPERATURE = "temperature"

    # Wind params:
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    WIND_GUSTS = "wind_gusts"


class WeatherModels(enum.Enum):
    """
    Weather models enum.
    """
    #: ICON model.
    MODEL_ICON = "icon"
    #: Default model.
    DEFAULT = "default"


@dataclass
class Forecast(BaseDomainModel):
    """
    Forecast domain model represents a forecast for a location for a given time interval.

    This object is part of the core domain of this project and will utilize various modules:
        1. Fetch the Forecast object with the ForecastService.
        2. Store Forecast object in repository.
        3. Apply domain logic to find the best forecast model for a given location.
    """

    #: A timestamp when the forecast was created.
    created_at: datetime
    #: A timestamp when the forecast is valid.
    valid_at: datetime
    #: Pandas DataFrame containing forecast data.
    data: pd.DataFrame
    #: Location for the forecast.
    location: Location
    #: Weather forecast model:
    model: WeatherModels
    #: Identifier
    id: Union[id, None] = None

    def set_id(self, identifier: int) -> None:
        if self.id:
            raise
        self.id = identifier

    def __eq__(self, other: "Forecast") -> bool:
        """
        data property is a DataFrame object that needs special treatment.
        TODO: This can be implemented smarter.

        :param other: Other element to compare with.
        :return: True if equal, false otherwise
        """
        if not isinstance(other, Forecast):
            return False
        return (
            self.id == other.id
            and self.created_at == other.created_at
            and self.valid_at == other.valid_at
            and all(self.data == other.data)
            and self.location == other.location
        )

