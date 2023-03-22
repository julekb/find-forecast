import os
from datetime import timedelta, datetime
import pytest


from src.adapters.windycom.client import WindyComClient
from src.adapters.openmeteo.client import OpenMeteoClient
from src.services import WindyComExternalService, OpenMeteoExternalService, ForecastService
from src.domain import Location, Forecast, ForecastParams

import pandas as pd


class TestCase:
    @pytest.fixture()
    def windycom_client(self):
        config = {
            "user": os.environ["METEOMATICS_USER"],
            "password": os.environ["METEOMATICS_PASSWORD"]
        }
        return WindyComClient(config=config)

    @pytest.fixture()
    def openmeteo_client(self):
        config = {}
        return OpenMeteoClient(config=config)

    def test_windycom_client(self, windycom_client):
        client = windycom_client
        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = client.get_forecast_data(
            target_timestamp=yesterday, extra_params=params, lon=lon, lat=lat
        )

        assert isinstance(forecast, float)

    def test_openmeteo_client(self, openmeteo_client):
        client = openmeteo_client
        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = client.get_forecast_data(
            target_timestamp=yesterday, extra_params=params, wind_params=[], lon=lon, lat=lat
        )

        assert isinstance(forecast, dict)

    def test_service(self, windycom_client):
        client = windycom_client
        service = WindyComExternalService(client=client)

        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = service.get_forecast(
            target_timestamp=yesterday, extra_params=params, lon=lon, lat=lat
        )
        assert isinstance(forecast, Forecast)

    def test_openmeteo_service(self, openmeteo_client):
        client = openmeteo_client
        service = OpenMeteoExternalService(client=client)

        forecast = service.get_forecast(
            target_timestamp=datetime.utcnow(),
            location=Location(lon="13.461804", lat="52.520551", name="test location"),
            params=[ForecastParams.WIND_SPEED, ForecastParams.WIND_DIRECTION, ForecastParams.TEMPERATURE]
        )

        assert isinstance(forecast, Forecast)
        assert isinstance(forecast.data, pd.DataFrame)

    def test_forecast_service(self, windycom_client):
        client = windycom_client
        external_service = WindyComExternalService(client=client)
        service = ForecastService(external_services=[external_service])
        location = Location(name="My location", lon="53.11", lat="21.37")
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = "t_2m:C"

        forecast = service.get_forecast_for_location(location=location, target_timestamp=yesterday, extra_params=params)

        assert isinstance(forecast, Forecast)
