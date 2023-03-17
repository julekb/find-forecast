from http import HTTPStatus
from requests.auth import HTTPBasicAuth
import abc
import datetime
import requests

from src.adapters.models import ForecastBaseClient
from src.dtos import ForecastDTO

METEOMATICS_API_URL = "https://api.meteomatics.com"


class WindyComClient(ForecastBaseClient):
    base_url: str
    user: str
    password: str

    def __init_service__(self, user, password, base_url=METEOMATICS_API_URL):
        self.base_url = base_url
        # this is not safe
        self.user = user
        self.password = password

    def get_forecast_data(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> ForecastDTO:
        response = requests.get(
            f"{self.base_url}/{str(target_timestamp.date())}T00:00:00Z/{extra_params}/{lon},{lat}/json",
            auth=HTTPBasicAuth(self.user, self.password))
        if response.status_code != HTTPStatus.OK:
            raise Exception(f'External call failed. Msg: {response.status_code} - {response.reason}')
        return ForecastDTO(response.json()["data"][0]["coordinates"][0]["dates"][0]["value"])
