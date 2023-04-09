import abc
import datetime
from typing import Dict, List


class BaseClient(abc.ABC):
    """Abstract base client class."""

    def __init__(self, config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_client__(**config)

    @abc.abstractmethod
    def __init_client__(self, *args, **kwargs):
        """Initialize client-specific entities."""


class ForecastBaseClient(BaseClient):
    """Abstract base forecast client class."""

    @abc.abstractmethod
    def get_forecast_data(
        self, lon: str, lat: str, target_timestamp: datetime.datetime, params: List, model: str
    ) -> Dict:
        """
        Get forcast data.

        :param lon: The location's longitude.
        :param lat: The location's latitude.
        :param target_timestamp:
        :param params: An array of requested weather parameters.
        :param model: Weather model.
        :return: A dictionary containing the requested weather data.
        """


class WeatherBaseClient(BaseClient):
    """Abstract base weather log client class."""

    @abc.abstractmethod
    def get_weather_data(self):
        """Get weather data."""
        pass
