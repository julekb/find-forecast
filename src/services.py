from dataclasses import dataclass
from typing import List
import abc
import datetime


from src.adapters.models import ForecastBaseClient
from src.domain import Location, Forecast, ConditionsDataPoint


@dataclass(frozen=True)
class ForecastData:
    value: str


class BaseService(abc.ABC):
    """Abstract base service class."""


class ExternalBaseService(BaseService):
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

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> ConditionsDataPoint:
        """Get forecast data from external service."""
        forecast_dto = self.client.get_forecast_data(
            target_timestamp=target_timestamp, extra_params=extra_params, lon=lon, lat=lat
        )
        forecast = ConditionsDataPoint(forecast_dto.value)

        return forecast


class ForecastService(BaseService):
    """Forecast service."""
    def __init__(self, external_services):
        self._external_services = {service.name: service for service in external_services}

    def get_external_service(self, service_name: str):
        """Get an external service implementation."""
        return self._external_services.get(service_name)

    @property
    def _external_services_names(self) -> List:
        """Get an array of names of external forecast services."""
        return list(self._external_services.keys())

    def get_forecast_for_location(self, location: Location, extra_params, target_timestamp) -> Forecast:
        """Get forecast service for a location."""
        external_service = self.get_external_service(self._external_services_names[0])
        cdp = external_service.get_forecast(
            target_timestamp=target_timestamp, extra_params=extra_params, lon=location.lon, lat=location.lat
        )

        forecast = Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=[cdp]
        )
        return forecast
