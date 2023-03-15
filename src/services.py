from dataclasses import dataclass
import abc
import datetime

from src.adapters.windycom.client import BaseClient


@dataclass(frozen=True)
class Forecast:
    value: str


class BaseService:
    """Base abstract service."""
    @abc.abstractmethod
    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> Forecast:
        """Get forecast data from external service."""


class WindyComService(BaseService):
    def __init__(self, client: BaseClient):
        self.client = client

    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> Forecast:
        forecast = self.client.get_forecast_data(
            target_timestamp=target_timestamp, extra_params=extra_params, lon=lon, lat=lat
        )
        forecast = Forecast(forecast[0]['coordinates'][0]['dates'][0])
        return forecast
