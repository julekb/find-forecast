from dataclasses import dataclass
from typing import List, Union
import abc
import datetime

from src.adapters.models import ForecastBaseClient
from src.domain import Location, Forecast, ForecastParams, WeatherModels
from src.utils import create_bijection_dict, InjectionDict
from src.services.common import BaseService

import pandas as pd


@dataclass(frozen=True)
class ForecastData:
    value: str


class ExternalBaseService(BaseService):
    """Base abstract service."""

    #: Service name.
    name: str
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP: InjectionDict
    #: Bijective domain-query models mapping.
    DOMAIN_TO_QUERY_MODELS_MAP: InjectionDict

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

    def translate_to_query_models(self, models: List) -> List:
        """
        Translate domain models for a client into query forecast params.

        :param models: Domain weather models.
        :return: Query weather models.
        """
        return [self.DOMAIN_TO_QUERY_MODELS_MAP[model] for model in models]

    def translate_to_domain_models(self, models: List) -> List:
        """
        Translate query models for a client into domain forecast params.

        :param models: Query weather models.
        :return: Domain weather models.
        """
        return [self.DOMAIN_TO_QUERY_MODELS_MAP.backward[model] for model in models]

    @abc.abstractmethod
    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: List,
        model: WeatherModels,
    ) -> Forecast:
        """Get forecast data from external service."""


class WindyComExternalService(ExternalBaseService):
    """External forecast service implementation for windy.com."""

    #: Service name.
    name = "WindyComExternalService"
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict({ForecastParams.TEMPERATURE: "t_2m:C"})
    DOMAIN_TO_QUERY_MODELS_MAP = create_bijection_dict({WeatherModels.DEFAULT: "mix"})

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: List,
        model: WeatherModels,
    ) -> Forecast:
        """Get forecast data from external service."""
        forecast_raw = self.client.get_forecast_data(
            lon=location.lon,
            lat=location.lat,
            target_timestamp=target_timestamp,
            params=self.translate_to_query_params(extra_params),
            model=self.translate_to_query_models([model])[0],
        )
        data = pd.DataFrame.from_dict({"value": [forecast_raw]})
        forecast = Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=data,
            location=location,
            weather_model=model,
        )

        return forecast


class OpenMeteoExternalService(ExternalBaseService):
    """External forecast service implementation for Open-Meteo."""

    #: Service name.
    name = "OpenMeteoExternalService"
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict(
        {
            ForecastParams.TEMPERATURE: "temperature_2m",
            ForecastParams.WIND_SPEED: "windspeed_10m",
            ForecastParams.WIND_DIRECTION: "winddirection_10m",
            ForecastParams.WIND_GUSTS: "windgusts_10m",
        }
    )
    DOMAIN_TO_QUERY_MODELS_MAP = create_bijection_dict({WeatherModels.MODEL_ICON: "icon_seamless"})

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: List,
        model: WeatherModels,
    ) -> Forecast:
        forecast_raw = self.client.get_forecast_data(
            lon=location.lon,
            lat=location.lat,
            target_timestamp=target_timestamp,
            params=self.translate_to_query_params(extra_params),
            model=self.translate_to_query_models([model])[0],
        )
        data = pd.DataFrame.from_dict(forecast_raw)
        data.rename(columns=self.DOMAIN_TO_QUERY_PARAMS_MAP.backward, inplace=True)
        forecast = Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=data,
            location=location,
            weather_model=model,
        )

        return forecast


class ForecastService(BaseService):
    """Forecast service implementation."""

    def __init__(self, external_services: List[ExternalBaseService]):
        self._external_services = {service.name: service for service in external_services}

    def get_external_service(self, service_name: str) -> Union[ExternalBaseService, None]:
        """Get an external service implementation."""
        return self._external_services.get(service_name)

    @property
    def _external_services_names(self) -> List:
        """Get an array of names of external forecast services."""
        return list(self._external_services.keys())

    def get_forecast_for_location(
        self, location: Location, extra_params, target_timestamp, model: WeatherModels
    ) -> Forecast:
        """Get forecast service for a location."""
        external_service = self.get_external_service(self._external_services_names[0])
        if not external_service:
            raise
        cdp = external_service.get_forecast(
            location=location,
            target_timestamp=target_timestamp,
            extra_params=extra_params,
            model=model,
        )

        forecast = Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=pd.DataFrame([cdp]),
            location=location,
            weather_model=model,
        )
        return forecast
