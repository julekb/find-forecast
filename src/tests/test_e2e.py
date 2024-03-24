import datetime

from domain.models import ForecastModels, WeatherParams
from scripts.run_weather_overview import run_weather_overview


def test_weather_overview_happy_path():
    target_location_name = "valencia"
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=3)
    end_date = now + datetime.timedelta(days=3)
    forecast_models = (ForecastModels.MODEL_ICON,)
    weather_params = (WeatherParams.TEMPERATURE,)

    run_weather_overview(
        location_name=target_location_name,
        start_date=start_date,
        end_date=end_date,
        weather_params=weather_params,
        forecast_models=forecast_models,
    )
