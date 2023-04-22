import abc
import enum
from typing import Union, List

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


class BaseDomainModel(abc.ABC):
    """Abstract base domain class."""


@dataclass(frozen=True)
class Location(BaseDomainModel):
    lon: str
    lat: str
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


class ForecastModels(enum.Enum):
    """
    Weather forecast models enum.
    """

    #: ICON model.
    MODEL_ICON = "icon"
    #: Default model.
    DEFAULT = "default"


@dataclass
class WeatherData(BaseDomainModel):
    #: Pandas DataFrame containing weather data.
    data: pd.DataFrame


@dataclass
class WeatherLog(WeatherData):
    """Weather data log."""

    source: str


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
    #: A timestamp when the forecast is valid.
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

        :param other: Other element to compare with.
        :return: True if equal, false otherwise
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


class ForecastAnalyzer(BaseDomainModel):
    def __init__(self, forecasts: list[Forecast]):
        self.forecasts = forecasts

    def analyze(self, forecasts: List[Forecast], weather_log: WeatherLog) -> None:
        """Analyze all forecasts against the weather log."""

    def get_winning_weather_model(self) -> ForecastModels:
        """Find a winning forecasting model."""
        pass


class ObservableLocation(BaseDomainModel):
    """
    The Observable Location domain object.

    Aggregates all the data needed for further processing.
    Consists of:
        - Weather Logs, (support for multiple logs can be added)
        - Forecasts,
        - Location.

    In the future this will be the Location model.
    """

    location: Location
    weather_log: WeatherLog
    forecasts: List[Forecast]
