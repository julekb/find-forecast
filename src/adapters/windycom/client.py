import requests
from requests.auth import HTTPBasicAuth

METEOMATICS_API_URL = "https://api.meteomatics.com"


class WindyComClient:
    base_url: str
    user: str
    password: str

    def __init__(self, user, password, base_url=METEOMATICS_API_URL):
        self.base_url = base_url
        # this is not safe
        self.user = user
        self.password = password

    def get_forecast_data(self, date_range, lon, lat):
        url = f"{self.base_url}/{date_range}/t_2m:C/{lon},{lat}/json"
        response = requests.get(url, auth=HTTPBasicAuth(self.user, self.password))
        return response.json()
