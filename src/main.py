import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from adapters.openmeteo.client import OpenMeteoClient
from constants import PLOTS_DIR
from domain.models import ForecastModels, Location, WeatherData, WeatherParams
from services.weather_services import OpenMeteoExternalService, WeatherService


def plot_weather_data_as_jpg(weather_data: WeatherData, filename: str) -> None:
    output_dir = os.path.join(PLOTS_DIR, filename)
    print(output_dir)

    sns.set_theme()
    sns.relplot(data=weather_data.data, kind="line")
    plt.savefig(output_dir, format="jpg", dpi=300)


if __name__ == "__main__":
    # bootstrap

    Path(PLOTS_DIR).mkdir(parents=True, exist_ok=True)

    windy_com_config: dict = {
        "user": os.environ["METEOMATICS_USER"],
        "password": os.environ["METEOMATICS_PASSWORD"],
    }
    open_meteo_service = OpenMeteoExternalService(client=OpenMeteoClient(config={}))

    location = Location(name="My location", lon="53.11", lat="21.37")
    timestamp = datetime.utcnow() + timedelta(days=1)

    forecast = open_meteo_service.get_forecast(
        location=location,
        extra_params=(WeatherParams.WIND_SPEED,),
        model=ForecastModels.MODEL_ICON,
        target_timestamp=timestamp,
        end_timestamp=timestamp,
    )

    ###########

    weather_service = WeatherService()
    location = Location(name="Valencia", lon="39.46975", lat="-0.37739")
    timestamp_end = datetime.today()
    timestamp_start = timestamp_end - timedelta(days=2)
    valencia_weather = weather_service.get_weather_for_location(
        location, timestamp_start, timestamp_end
    )

    plot_weather_data_as_jpg(valencia_weather, "valencia_weather.jpg")

    print("Done.")
