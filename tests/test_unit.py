import os
from datetime import timedelta, datetime, date
import pytest
import shutil
from random import randint
import pickle as pkl

from src.adapters.openmeteo.client import OpenMeteoClient
from src.adapters.windycom.client import WindyComClient
from src.domain.models import Location, Forecast, ForecastParams, ForecastModels
from src.services.forecast_services import (
    WindyComExternalService,
    OpenMeteoExternalService,
)
from src.repositories import PklRepository

import pandas as pd


class TestCase:
    @pytest.fixture()
    def windycom_client(self):
        return WindyComClient(
            config={
                "user": os.environ["METEOMATICS_USER"],
                "password": os.environ["METEOMATICS_PASSWORD"],
            }
        )

    @pytest.fixture()
    def openmeteo_client(self):
        config = {}
        return OpenMeteoClient(config=config)

    def test_windycom_client(self, windycom_client):
        client = windycom_client
        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = ["t_2m:C"]
        model = "mix"

        forecast = client.get_forecast_data(
            lon=lon, lat=lat, target_timestamp=yesterday, params=params, model=model
        )

        assert isinstance(forecast, float)

    def test_openmeteo_client_get_forecast(self, openmeteo_client):
        client = openmeteo_client
        lon = "13.461804"
        lat = "52.520551"
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = ["temperature_2m"]
        model = "icon_seamless"

        forecast = client.get_forecast_data(
            lon=lon, lat=lat, target_timestamp=yesterday, params=params, model=model
        )

        assert isinstance(forecast, dict)

    def test_openmeteo_client_get_historical_data(self, openmeteo_client):
        client = openmeteo_client
        lon = "13.461804"
        lat = "52.520551"
        start_date = date.today() - timedelta(days=4)
        end_date = date.today()
        params = ["temperature_2m"]
        model = "icon_seamless"

        forecast = client.get_historical_data(
            lon=lon, lat=lat, start_date=start_date, end_date=end_date, params=params, model=model
        )

        assert isinstance(forecast, dict)

    def test_service(self, windycom_client, example_location):
        client = windycom_client
        service = WindyComExternalService(client=client)

        yesterday = datetime.utcnow() - timedelta(days=1)
        params = [ForecastParams.TEMPERATURE]

        forecast = service.get_forecast(
            location=example_location,
            target_timestamp=yesterday,
            extra_params=params,
            model=ForecastModels.DEFAULT,
        )

        assert isinstance(forecast, Forecast)

    def test_openmeteo_service(self, openmeteo_client, example_location):
        client = openmeteo_client
        service = OpenMeteoExternalService(client=client)
        params = [
            ForecastParams.WIND_SPEED,
            ForecastParams.WIND_DIRECTION,
            ForecastParams.TEMPERATURE,
        ]

        forecast = service.get_forecast(
            target_timestamp=datetime.utcnow(),
            location=example_location,
            extra_params=params,
            model=ForecastModels.MODEL_ICON,
        )

        assert isinstance(forecast, Forecast)
        assert isinstance(forecast.data, pd.DataFrame)

    def test_forecast_service(self, windycom_client, forecast_service, example_location):
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = [ForecastParams.TEMPERATURE]
        model = ForecastModels.DEFAULT

        forecast = forecast_service.get_forecast_for_location(
            location=example_location, target_timestamp=yesterday, extra_params=params, model=model
        )

        assert isinstance(forecast, Forecast)
        assert isinstance(forecast, Forecast)


class TestCaseRepository:
    BASE_DIR = "_test/"
    STORAGE_DIR = "storage/"

    def _forecast(self, fid):
        obj = Forecast(
            id=fid,
            created_at=datetime.now(),
            valid_at=datetime.now(),
            location=Location(name="A location", lon="11.22", lat="22.11"),
            data=pd.DataFrame(
                {ForecastParams.TEMPERATURE: [10, 11, 12], ForecastParams.WIND_SPEED: [15, 18, 18]}
            ),
            weather_model=ForecastModels.DEFAULT,
        )
        return obj

    @pytest.fixture()
    def forecast(self):
        return self._forecast(None)

    @pytest.fixture()
    def forecast_with_id(self):
        return self._forecast(randint(1, 10000))

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        os.makedirs(self.BASE_DIR + self.STORAGE_DIR)

        # run the test
        yield

        shutil.rmtree(self.BASE_DIR)

    def test_repository_save_forecast(self, forecast):
        repository = PklRepository(base_dir=self.BASE_DIR + self.STORAGE_DIR)

        saved_forecast = repository.save_forecast(forecast)

        assert os.path.isfile("_test/storage/forecast_1.pkl")
        assert saved_forecast.id == 1

    def test_repository_retrieve_forecast(self, forecast):
        repository = PklRepository(base_dir="_test/storage")
        with open(f"{self.BASE_DIR}{self.STORAGE_DIR}forecast_{str(forecast.id)}.pkl", "wb") as f:
            pkl.dump(forecast, f)

        retrieved = repository.retrieve_forecast(forecast.id)

        assert retrieved == forecast

    def test_repository_get_last_forecast_id(self, forecast):
        repository = PklRepository(base_dir="_test/storage")
        with open(f"{self.BASE_DIR}{self.STORAGE_DIR}forecast_1.pkl", "wb") as f:
            pkl.dump("", f)
        with open(f"{self.BASE_DIR}{self.STORAGE_DIR}forecast_2.pkl", "wb") as f:
            pkl.dump("", f)
        with open(f"{self.BASE_DIR}{self.STORAGE_DIR}notforcast_1.pkl", "wb") as f:
            pkl.dump("", f)

        max_id = repository._get_last_forecast_id()

        assert max_id == 2
