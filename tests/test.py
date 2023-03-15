import os
from datetime import timedelta, datetime
import pytest


from src.adapters.windycom.client import WindyComClient
from src.services import WindyComService, Forecast


class TestCase:
    @pytest.fixture()
    def client(self):
        return WindyComClient(
            user=os.environ["METEOMATICS_USER"],
            password=os.environ["METEOMATICS_PASSWORD"]
        )

    def test_client(self, client):
        print(client)
        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = client.get_forecast_data(
            target_timestamp=yesterday, extra_params=params, lon=lon, lat=lat
        )

        assert isinstance(forecast, list)

    def test_service(self, client):
        print(client)
        service = WindyComService(client=client)

        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = service.get_forecast(
            target_timestamp=yesterday, extra_params=params, lon=lon, lat=lat
        )
        assert isinstance(forecast, Forecast)
