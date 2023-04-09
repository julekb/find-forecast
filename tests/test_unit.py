import os
from datetime import timedelta, datetime
import pytest
import shutil
from random import randint
import pickle as pkl

from src.adapters.openmeteo.client import OpenMeteoClient
from src.adapters.windycom.client import WindyComClient
from src.domain import Location, Forecast, ForecastParams, WeatherModels
from src.services.forecast_services import (
    WindyComExternalService,
    OpenMeteoExternalService,
    ForecastService,
)
from src.repositories import PklRepository

import pandas as pd


class TestCase:
    @pytest.fixture()
    def windycom_client(self):
        config = {
            "user": os.environ["METEOMATICS_USER"],
            "password": os.environ["METEOMATICS_PASSWORD"],
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
        params = ["t_2m:C"]
        model = "mix"

        forecast = client.get_forecast_data(
            lon=lon, lat=lat, target_timestamp=yesterday, params=params, model=model
        )

        assert isinstance(forecast, float)

    def test_openmeteo_client(self, openmeteo_client):
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

    def test_service(self, windycom_client):
        client = windycom_client
        service = WindyComExternalService(client=client)

        yesterday = datetime.utcnow() - timedelta(days=1)
        params = [ForecastParams.TEMPERATURE]
        location = Location(name="Some location", lon="13.461804", lat="52.520551")

        forecast = service.get_forecast(
            location=location,
            target_timestamp=yesterday,
            extra_params=params,
            model=WeatherModels.DEFAULT,
        )
        assert isinstance(forecast, Forecast)

    def test_openmeteo_service(self, openmeteo_client):
        client = openmeteo_client
        service = OpenMeteoExternalService(client=client)
        params = [
            ForecastParams.WIND_SPEED,
            ForecastParams.WIND_DIRECTION,
            ForecastParams.TEMPERATURE,
        ]

        forecast = service.get_forecast(
            target_timestamp=datetime.utcnow(),
            location=Location(lon="13.461804", lat="52.520551", name="test location"),
            extra_params=params,
            model=WeatherModels.MODEL_ICON,
        )

        assert isinstance(forecast, Forecast)
        assert isinstance(forecast.data, pd.DataFrame)

    def test_forecast_service(self, windycom_client):
        client = windycom_client
        external_service = WindyComExternalService(client=client)
        service = ForecastService(external_services=[external_service])
        location = Location(name="My location", lon="53.11", lat="21.37")
        yesterday = datetime.utcnow() - timedelta(days=1)
        params = [ForecastParams.TEMPERATURE]
        model = WeatherModels.DEFAULT

        forecast = service.get_forecast_for_location(
            location=location, target_timestamp=yesterday, extra_params=params, model=model
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
            model=WeatherModels.DEFAULT,
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

        retrieved = repository.retrieve_forecast_by_id(id=forecast.id)

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
