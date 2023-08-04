import datetime
import os

from src.adapters.openmeteo.client import OpenMeteoClient
from src.adapters.windycom.client import WindyComClient
from src.domain.functions import construct_forecast_analyser
from src.domain.models import Location, ForecastModels, ForecastParams
from src.services.forecast_services import ForecastService, WindyComExternalService, OpenMeteoExternalService

if __name__ == "__main__":

    # bootstrap
    windy_com_config: dict = {
            "user": os.environ["METEOMATICS_USER"],
            "password": os.environ["METEOMATICS_PASSWORD"],
        }
    windy_com_service = WindyComExternalService(client=WindyComClient(config=windy_com_config))
    open_meteo_service = OpenMeteoExternalService(client=OpenMeteoClient(config={}))
    forecast_service = ForecastService(external_services=[windy_com_service, open_meteo_service])

    location = Location(name="My location", lon="53.11", lat="21.37")

    forecast_source_and_models = [
        {"forecast_service_name": "OpenMeteoExternalService", "model_name": ForecastModels.MODEL_ICON},
        {"forecast_service_name": "WindyComExternalService", "model_name": ForecastModels.DEFAULT},
    ]

    analyser = construct_forecast_analyser(
        service=forecast_service,
        forecast_source_and_models=forecast_source_and_models,
        params=ForecastParams.TEMPERATURE,
        location=location, target_timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )

    print("Done.")

