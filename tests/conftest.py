import os

import pytest

from src.adapters.openmeteo.client import OpenMeteoClient
from src.adapters.windycom.client import WindyComClient
from src.domain.models import Location
from src.services.weather_services import (ForecastService,
                                           OpenMeteoExternalService,
                                           WindyComExternalService)


@pytest.fixture()
def example_location():
    return Location(name="My location", lon="53.11", lat="21.37")


@pytest.fixture()
def forecast_service():
    windycom_client = WindyComClient(
        config={
            "user": os.environ["METEOMATICS_USER"],
            "password": os.environ["METEOMATICS_PASSWORD"],
        }
    )
    windycom_service = WindyComExternalService(client=windycom_client)

    openmeteo_client = OpenMeteoClient(config={})
    openmeteo_service = OpenMeteoExternalService(client=openmeteo_client)

    return ForecastService(external_services=[windycom_service, openmeteo_service])
