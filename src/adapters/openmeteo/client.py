import datetime
import os
from http import HTTPStatus
from typing import Iterable

import requests

from src.adapters.models import ForecastBaseClient


class OpenMeteoClient(ForecastBaseClient):
    base_url: str
    archive_base_url: str

    def __init_client__(
        self,
        base_url=os.environ["OPENMETEO_API_URL"],
        archive_base_url=os.environ["OPENMETEO_ARCHIVE_API_URL"],
    ):
        self.base_url = base_url
        self.archive_base_url = archive_base_url

    def get_forecast_data(
        self, lon: str, lat: str, target_timestamp: datetime.datetime, params: Iterable, model: str
    ) -> dict:
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

    def get_historical_data(
        self,
        lon: str,
        lat: str,
        start_date: datetime.date,
        end_date: datetime.date,
        params: list,
        model: str,
    ) -> dict:
        query_params = (
            ("latitude", lat),
            ("longitude", lon),
            ("start_date", str(start_date)),
            ("end_date", str(end_date)),
            ("hourly", ",".join(params)),
            ("models", str(model)),
            ("windspeed_unit", "kn"),
        )
        response = requests.get(self.base_url, params=query_params)
        if response.status_code != HTTPStatus.OK:
            raise Exception(f"External call failed. Msg: {response.status_code} - {response.text}")
        return response.json()["hourly"]
