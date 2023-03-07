import os

from adapters.windycom.client import WindyComClient


if __name__ == '__main__':
    c = WindyComClient(
        user=os.environ["METEOMATICS_USER"],
        password=os.environ["METEOMATICS_PASSWORD"]
    )

    lon = "13.461804"
    lat = "52.520551"
    date_range = "2023-03-06T00:00:00Z--2023-03-09T00:00:00Z:PT1H"

    forecast = c.get_forecast_data(date_range=date_range, lon=lon, lat=lat)
    print(forecast)


