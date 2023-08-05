import abc
import datetime


class BaseClient(abc.ABC):
    def __init__(self, config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_client__(**config)

    @abc.abstractmethod
    def __init_client__(self, *args, **kwargs):
        ...


class ForecastBaseClient(BaseClient):
    @abc.abstractmethod
    def get_forecast_data(
        self, lon: str, lat: str, target_timestamp: datetime.datetime, params: list, model: str
    ) -> dict:
        ...


class WeatherBaseClient(BaseClient):
    @abc.abstractmethod
    def get_weather_data(self):
        ...
