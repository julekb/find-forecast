from http import HTTPStatus
import datetime
import requests
import os

from src.adapters.models import ForecastBaseClient
from src.dtos import ForecastDTO


class OpenMeteoClient(ForecastBaseClient):
    base_url: str

    def __init_service__(self, base_url=os.environ["OPENMETEO_API_URL"]):
        self.base_url = base_url

    def get_forecast_data(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> ForecastDTO:
        response = requests.get(self.base_url + "?latitude=52.52&longitude=13.41&hourly=temperature_2m")
        if response.status_code != HTTPStatus.OK:
            raise Exception(f'External call failed. Msg: {response.status_code} - {response.reason}')
        return ForecastDTO(response.json()["hourly"]["temperature_2m"][0])
