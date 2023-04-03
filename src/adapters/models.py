import abc
import datetime
from typing import Dict, List


class ForecastBaseClient(abc.ABC):
    """Abstract base client class."""

    def __init__(self, config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_service__(**config)

    @abc.abstractmethod
    def __init_service__(self, *args, **kwargs):
        """Initialize service-specific entities."""

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
