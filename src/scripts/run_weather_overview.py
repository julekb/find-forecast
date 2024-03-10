import datetime
from pathlib import Path
from typing import Sequence

from adapters.openmeteo.client import OpenMeteoClient
from constants import PLOTS_DIR
from domain.models import ForecastModels, WeatherParams
from locations_data import locations as locations_data
from plotting import plot_weather_data_as_jpg
from repositories import LocationRepository
from services.weather_services import OpenMeteoExternalService, WeatherService


def run_weather_overview(
    location_name: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    weather_params: Sequence[WeatherParams],
    forecast_model: ForecastModels,
) -> None:
    if len(weather_params) == 0:
        raise Exception("Weather params sequence can't be empty.")

    if len(weather_params) > 1:
        raise NotImplementedError

    Path(PLOTS_DIR).mkdir(parents=True, exist_ok=True)

    locations_repository = LocationRepository(locations_data)
    weather_service = WeatherService()
    open_meteo_service = OpenMeteoExternalService(client=OpenMeteoClient(config={}))

    location = locations_repository.get_location(location_name)
    now = datetime.datetime.utcnow()

    weather = weather_service.get_weather_for_location(location, start_date, now)
    forecast = open_meteo_service.get_forecast(
        location, now, end_date, weather_params, forecast_model
    )

    composite_data = weather + forecast

    plot_weather_data_as_jpg(composite_data, weather_params[0], "weather_and_forecast.jpg")


if __name__ == "__main__":
    print("Starting weather overview script.")

    target_location_name = "valencia"
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=3)
    end_date = now + datetime.timedelta(days=3)
    forecast_model = ForecastModels.MODEL_ICON
    weather_params = (WeatherParams.TEMPERATURE,)

    run_weather_overview(
        location_name=target_location_name,
        start_date=start_date,
        end_date=end_date,
        weather_params=weather_params,
        forecast_model=forecast_model,
    )

    print("Weather overview script finished.")
