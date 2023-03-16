from dataclasses import dataclass
from typing import List
import abc
import datetime


from src.adapters.windycom.client import BaseClient
from src.domain import Location, Forecast, ConditionsDataPoint


@dataclass(frozen=True)
class ForecastData:
    value: str


class ExternalBaseService:
    """Base abstract service."""

    name: str

    @abc.abstractmethod
    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> Forecast:
        """Get forecast data from external service."""


class WindyComExternalService(ExternalBaseService):
    """External forecast service for windy.com."""
    name = "WindyComExternalService"

    def __init__(self, client: BaseClient):
        self.client = client

    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> ConditionsDataPoint:
        forecast = self.client.get_forecast_data(
            target_timestamp=target_timestamp, extra_params=extra_params, lon=lon, lat=lat
        )
        forecast = ConditionsDataPoint(forecast[0]['coordinates'][0]['dates'][0])
        return forecast


class ForecastService:
    """Forecast service."""
    def __init__(self, external_services):
        self.external_services = {service.name: service for service in external_services}

    def get_external_service(self, service_name: str):
        return self.external_services.get(service_name)

    @property
    def external_services_names(self) -> List:
        return list(self.external_services.keys())

    def get_forecast_for_location(self, location: Location, extra_params, target_timestamp) -> Forecast:
        external_service = self.get_external_service(self.external_services_names[0])
        raw_forecast = external_service.get_forecast(
            target_timestamp=target_timestamp, extra_params=extra_params, lon=location.lon, lat=location.lat
        )

        forecast = Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=[{raw_forecast.wind_speed['date']: raw_forecast.wind_speed['value']}]
        )
        return forecast
