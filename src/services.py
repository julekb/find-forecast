from dataclasses import dataclass
from typing import List
import abc
import datetime


from src.adapters.models import ForecastBaseClient
from src.domain import Location, Forecast, ForecastParams
from src.utils import create_bijection_dict, InjectionDict

import pandas as pd


@dataclass(frozen=True)
class ForecastData:
    value: str


class BaseService(abc.ABC):
    """Abstract base service class."""


class ExternalBaseService(BaseService):
    """Base abstract service."""

    #: Service name.
    name: str
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP: InjectionDict

    def translate_to_query_params(self, params: List) -> List:
        """
        Translate domain forecast params into query params for a client.

        :param params: Domain forecast params.
        :return: Query params.
        """
        return [self.DOMAIN_TO_QUERY_PARAMS_MAP[param] for param in params]

    def translate_to_domain_params(self, params: List) -> List:
        """
        Translate query params for a client into domain forecast params.

        :param params: Query params.
        :return: Domain forecast params.
        """
        return [self.DOMAIN_TO_QUERY_PARAMS_MAP.backward[param] for param in params]

    @abc.abstractmethod
    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> Forecast:
        """Get forecast data from external service."""


class WindyComExternalService(ExternalBaseService):
    """External forecast service for windy.com."""
    #: Service name.
    name = "WindyComExternalService"
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP = {
        ForecastParams.TEMPERATURE: "t_2m:C"
    }

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> Forecast:
        """Get forecast data from external service."""
        forecast_raw = self.client.get_forecast_data(
            target_timestamp=target_timestamp, extra_params=extra_params, lon=lon, lat=lat
        )
        data = pd.DataFrame.from_dict({"value": [forecast_raw]})
        forecast = Forecast(created_at=datetime.datetime.now(), valid_at=datetime.datetime.now(), data=data)

        return forecast


class OpenMeteoExternalService(ExternalBaseService):
    #: Service name.
    name = "OpenMeteoExternalService"
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict({
        ForecastParams.TEMPERATURE: "temperature_2m",
        ForecastParams.WIND_SPEED: "windspeed_10m",
        ForecastParams.WIND_DIRECTION: "winddirection_10m",
        ForecastParams.WIND_GUSTS: "windgusts_10m"
    })

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
        self,
        target_timestamp: datetime.datetime,
        location: Location,
        params: List[ForecastParams]
    ) -> Forecast:
        forecast_raw = self.client.get_forecast_data(
            target_timestamp=target_timestamp,
            extra_params="",
            wind_params=self.translate_to_query_params(params),
            lon=location.lon,
            lat=location.lat
        )
        data = pd.DataFrame.from_dict(forecast_raw)
        data.rename(columns=self.DOMAIN_TO_QUERY_PARAMS_MAP.backward, inplace=True)
        forecast = Forecast(created_at=datetime.datetime.now(), valid_at=datetime.datetime.now(), data=data)
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
