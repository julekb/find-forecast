from http import HTTPStatus
import datetime
import requests
import os
from typing import Dict, List

from src.adapters.models import ForecastBaseClient


class OpenMeteoClient(ForecastBaseClient):
    base_url: str

    def __init_service__(self, base_url=os.environ["OPENMETEO_API_URL"]):
        self.base_url = base_url

    def get_forecast_data(
            self, target_timestamp: datetime.datetime, extra_params: str, wind_params: List, lon: str, lat: str
    ) -> Dict:
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": 7,
            "hourly": ",".join(wind_params)
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code != HTTPStatus.OK:
            raise Exception(f'External call failed. Msg: {response.status_code} - {response.reason}')
        return response.json()["hourly"]
