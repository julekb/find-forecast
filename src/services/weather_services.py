import abc
import datetime
from dataclasses import dataclass
from typing import Iterable

import meteostat
import pandas as pd

from adapters.models import ForecastBaseClient
from domain.models import (Forecast, ForecastModels, Location, WeatherData,
                           WeatherParams)
from utils import InjectionDict, create_bijection_dict


@dataclass(frozen=True)
class ForecastData:
    value: str


class ExternalBaseService:
    name: str
    DOMAIN_TO_QUERY_PARAMS_MAP: InjectionDict
    DOMAIN_TO_QUERY_MODELS_MAP: InjectionDict

    @classmethod
    def _translate(cls, mapper, params):
        try:
            return [mapper[param] for param in params]
        except KeyError as error:
            raise Exception(
                f"{cls.__name__}: Object {error.args[0]} not found in mapper values {mapper.keys()}"
            )

    def translate_to_query_params(self, params: Iterable) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_PARAMS_MAP, params)

    def translate_to_domain_params(self, params: Iterable) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_PARAMS_MAP.backward, params)

    def translate_to_query_models(self, models: Iterable) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_MODELS_MAP, models)

    def translate_to_domain_models(self, models: Iterable) -> list:
        return self._translate(self.DOMAIN_TO_QUERY_MODELS_MAP.backward, models)


class ExternalWeatherBaseService(ExternalBaseService):
    @abc.abstractmethod
    def get_weather(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        extra_params: Iterable,
    ):
        ...


class ExternalForecastBaseService(ExternalBaseService):
    @abc.abstractmethod
    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        end_timestamp: datetime.datetime,
        extra_params: Iterable,
        model: ForecastModels,
    ) -> Forecast:
        ...


class MeteostatWeatherService(ExternalBaseService):
    name = "MeteostatsWeatherExternalService"
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict({WeatherParams.TEMPERATURE: "temp"})

    def _to_obj(self, data) -> pd.DataFrame:
        if data.index.name != "time":
            raise Exception("Unexpected index name.")

        data.index.name = WeatherParams.TIMESTAMP.value
        data.rename(columns=self.DOMAIN_TO_QUERY_PARAMS_MAP.backward, inplace=True)
        return data[self.DOMAIN_TO_QUERY_PARAMS_MAP.backward.values()]

    @staticmethod
    def _to_locations(data: pd.DataFrame) -> list[Location]:
        stations_by_id = data.transpose().to_dict()
        return [
            Location(
                name=station_dict["name"] + " station",
                lon=str(station_dict["longitude"]),
                lat=str(station_dict["latitude"]),
            )
            for station_dict in stations_by_id.values()
        ]

    def get_weather(
        self,
        location: Location,
        timestamp_start: datetime.datetime,
        timestamp_end: datetime.datetime,
    ):
        stations = meteostat.Stations()
        stations = stations.nearby(lat=float(location.lat), lon=float(location.lon))
        station = stations.fetch(1)
        data = meteostat.Hourly(station, timestamp_start, timestamp_end).fetch()
        return self._to_obj(data)

    def find_stations_for_location(self, location: Location, n: int = 5) -> list[Location]:
        stations = meteostat.Stations()
        stations = stations.nearby(float(location.lon), float(location.lat))
        stations = stations.fetch(n)
        return self._to_locations(stations)


class WindyComExternalService(ExternalForecastBaseService):
    name = "WindyComExternalService"
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict({WeatherParams.TEMPERATURE: "t_2m:C"})
    DOMAIN_TO_QUERY_MODELS_MAP = create_bijection_dict({ForecastModels.DEFAULT: "mix"})

    def __init__(self, client: ForecastBaseClient):
        self.client = client

    def get_forecast(
        self,
        location: Location,
        target_timestamp: datetime.datetime,
        end_timestamp: datetime.datetime,
        extra_params: Iterable,
        model: ForecastModels,
    ) -> Forecast:
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


class OpenMeteoExternalService(ExternalForecastBaseService):
    name = "OpenMeteoExternalService"
    DOMAIN_TO_QUERY_PARAMS_MAP = create_bijection_dict(
        {
            WeatherParams.TEMPERATURE: "temperature_2m",
            WeatherParams.WIND_SPEED: "windspeed_10m",
            WeatherParams.WIND_DIRECTION: "winddirection_10m",
            WeatherParams.WIND_GUSTS: "windgusts_10m",
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
        end_timestamp: datetime.datetime,
        extra_params: Iterable,
        model: ForecastModels,
    ) -> Forecast:
        forecast_raw = self.client.get_forecast_data(
            lon=location.lon,
            lat=location.lat,
            target_timestamp=target_timestamp,
            params=self.translate_to_query_params(extra_params),
            model=self.translate_to_query_models([model])[0],
        )

        forecast_raw["time"] = [
            datetime.datetime.fromisoformat(timestamp_str) for timestamp_str in forecast_raw["time"]
        ]
        data = pd.DataFrame.from_dict(forecast_raw)

        data.rename(columns=self.DOMAIN_TO_QUERY_PARAMS_MAP.backward, inplace=True)
        data.rename(columns={"time": WeatherParams.TIMESTAMP}, inplace=True)
        data.set_index(WeatherParams.TIMESTAMP, inplace=True)

        data = data[:end_timestamp]  # type: ignore

        forecast = Forecast(
            created_at=datetime.datetime.now(),
            valid_at=datetime.datetime.now(),
            data=data,
            location=location,
            weather_model=model,
        )

        return forecast


class WeatherService:
    def __init__(self):
        self.external_service = MeteostatWeatherService()

    def get_weather_for_location(
        self,
        location: Location,
        timestamp_start: datetime.datetime,
        timestamp_end: datetime.datetime,
    ) -> WeatherData:
        data = self.external_service.get_weather(location, timestamp_start, timestamp_end)
        data = WeatherData(data=data, location=location)
        return data

    def get_nearest_station_location(self, location: Location) -> Location:
        return self.external_service.find_stations_for_location(location, 1)[0]


class ForecastService:
    def __init__(self, external_services: list[ExternalForecastBaseService]):
        self._external_services = {service.name: service for service in external_services}

    def get_external_service(self, service_name: str) -> ExternalForecastBaseService:
        try:
            return self._external_services[service_name]
        except KeyError:
            raise Exception(f"External service {service_name} not found.")

    @property
    def _external_services_names(self) -> list[str]:
        return list(self._external_services.keys())

    def get_forecast_for_location(
        self,
        location: Location,
        extra_params,
        target_timestamp,
        model: ForecastModels,
        external_service_name: str,
    ) -> Forecast:
        external_service = self.get_external_service(external_service_name)

        cdp = external_service.get_forecast(
            location=location,
            target_timestamp=target_timestamp,
            end_timestamp=target_timestamp + datetime.timedelta(days=7),  # TODO
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
