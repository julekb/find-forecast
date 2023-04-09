from http import HTTPStatus
import datetime
import requests
import os
from typing import Dict, List

from src.adapters.models import ForecastBaseClient


class OpenMeteoClient(ForecastBaseClient):
    """Open-Meteo API client."""

    base_url: str

    def __init_client__(self, base_url=os.environ["OPENMETEO_API_URL"]):
        self.base_url = base_url

    def get_forecast_data(
        self, lon: str, lat: str, target_timestamp: datetime.datetime, params: List, model: str
    ) -> Dict:
        query_params = (
            ("latitude", lat),
            ("longitude", lon),
            ("forecast_days", 7),
            ("hourly", ",".join(params)),
            ("models", str(model)),
            ("windspeed_unit", "kn"),
        )
        response = requests.get(self.base_url, params=query_params)
        if response.status_code != HTTPStatus.OK:
            raise Exception(f"External call failed. Msg: {response.status_code} - {response.text}")
        return response.json()["hourly"]
