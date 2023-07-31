from dataclasses import dataclass
from typing import Union
import abc
import datetime

from src.adapters.models import ForecastBaseClient
from src.domain.models import Location, Forecast, ForecastParams, ForecastModels
from src.utils import create_bijection_dict, InjectionDict
from src.services.common import BaseService

import pandas as pd


@dataclass(frozen=True)
class ForecastData:
    value: str


class ExternalBaseService(BaseService):
    #: Service name.
    name: str
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP: InjectionDict
    #: Bijective domain-query models mapping.
    DOMAIN_TO_QUERY_MODELS_MAP: InjectionDict

    @classmethod
    def _translate(cls, mapper, params):
        try:
            return [mapper[param] for param in params]
        except KeyError as error:
            raise Exception(
                f"{cls.__name__}: Object {error.args[0]} not found in mapper values {mapper.keys()}"
            )

    def translate_to_query_params(self, params: list) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_PARAMS_MAP, params)

    def translate_to_domain_params(self, params: list) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_PARAMS_MAP.backward, params)

    def translate_to_query_models(self, models: list) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_MODELS_MAP, models)

    def translate_to_domain_models(self, models: list) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_MODELS_MAP.backward, models)

    @abc.abstractmethod
    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: list,
        model: ForecastModels,
    ) -> Forecast:
        """Get forecast data from external service."""


class WindyComExternalService(ExternalBaseService):
    """External forecast service implementation for windy.com."""

    #: Service name.
    name = "WindyComExternalService"
    #: Bijective domain-query params mapping.
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict({ForecastParams.TEMPERATURE: "t_2m:C"})
    DOMAIN_TO_QUERY_MODELS_MAP = create_bijection_dict({ForecastModels.DEFAULT: "mix"})

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: list,
        model: ForecastModels,
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
    DOMAIN_TO_QUERY_MODELS_MAP = create_bijection_dict(
        {
            ForecastModels.DEFAULT: "gfs",
            ForecastModels.MODEL_ICON: "icon_seamless",
        }
    )

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: list,
        model: ForecastModels,
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
    def __init__(self, external_services: list[ExternalBaseService]):
        self._external_services = {service.name: service for service in external_services}

    def get_external_service(self, service_name: str) -> Union[ExternalBaseService, None]:
        try:
            return self._external_services[service_name]
        except KeyError:
            raise Exception(f"External service {service_name} not found.")

    @property
    def _external_services_names(self) -> list:
        return list(self._external_services.keys())

    def get_forecast_for_location(
        self, location: Location, extra_params, target_timestamp, model: ForecastModels
    ) -> Forecast:
        external_service = self.get_external_service(self._external_services_names[0])
        if not external_service:
            raise
        cdp = external_service.get_forecast(
            location=location,
            target_timestamp=target_timestamp,
            extra_params=extra_params,
            model=model,
        )

        return Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=pd.DataFrame([cdp]),
            location=location,
            weather_model=model,
        )
