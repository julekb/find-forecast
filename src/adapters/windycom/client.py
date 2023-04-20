from http import HTTPStatus
from requests.auth import HTTPBasicAuth
import os
import datetime
import requests
from typing import Dict, List

from src.adapters.models import ForecastBaseClient


class WindyComClient(ForecastBaseClient):
    """Windy.com API client."""

    base_url: str
    user: str
    password: str

    def __init_client__(self, user, password, base_url=os.environ["METEOMATICS_API_URL"]):
        self.base_url = base_url
        # this is not safe
        self.user = user
        self.password = password

    def get_forecast_data(
        self, lon: str, lat: str, target_timestamp: datetime.datetime, params: List, model: str
    ) -> Dict:
        query_params = {"model": model}
        date = str(target_timestamp.date())
        response = requests.get(
            f"{self.base_url}/{date}T00:00:00Z/{','.join(params)}/{lon},{lat}/json",
            auth=HTTPBasicAuth(self.user, self.password),
            params=query_params,
        )
        if response.status_code != HTTPStatus.OK:
            raise Exception(f"External call failed. Msg: {response.status_code} - {response.text}")

        return response.json()["data"][0]["coordinates"][0]["dates"][0]["value"]
