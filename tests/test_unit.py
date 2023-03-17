import os
from datetime import timedelta, datetime
import pytest


from src.adapters.windycom.client import WindyComClient
from src.services import WindyComExternalService, ForecastService
from src.domain import Location, Forecast, ConditionsDataPoint
from src.dtos import ForecastDTO


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

        assert isinstance(forecast, ForecastDTO)

    def test_service(self, client):
        service = WindyComExternalService(client=client)

        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = service.get_forecast(
            target_timestamp=yesterday, extra_params=params, lon=lon, lat=lat
        )
        assert isinstance(forecast, ConditionsDataPoint)

    def test_forecast_service(self, client):
        external_service = WindyComExternalService(client=client)
        service = ForecastService(external_services=[external_service])
        location = Location(name="My location", lon="53.11", lat="21.37")
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = service.get_forecast_for_location(location=location, target_timestamp=yesterday, extra_params=params)

        assert isinstance(forecast, Forecast)
