from http import HTTPStatus
from requests.auth import HTTPBasicAuth
import abc
import datetime
import requests

METEOMATICS_API_URL = "https://api.meteomatics.com"


class BaseClient:
    """Abstract base client class."""
    @abc.abstractmethod
    def get_forecast_data(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> dict:
        """Get forcast data"""


class WindyComClient(BaseClient):
    base_url: str
    user: str
    password: str

    def __init__(self, user, password, base_url=METEOMATICS_API_URL):
        self.base_url = base_url
        # this is not safe
        self.user = user
        self.password = password

    def get_forecast_data(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str
    ) -> dict:
        response = requests.get(
            f"{self.base_url}/{str(target_timestamp.date())}T00:00:00Z/{extra_params}/{lon},{lat}/json",
            auth=HTTPBasicAuth(self.user, self.password))
        if response.status_code != HTTPStatus.OK:
            raise Exception(f'External call failed. Msg: {response.status_code} - {response.reason}')
        return response.json()["data"]
