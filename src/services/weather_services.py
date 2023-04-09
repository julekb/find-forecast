from src.services.common import BaseService
from src.adapters.models import WeatherBaseClient
from src.domain import WeatherLog


class WeatherService(BaseService):
    """Weather service class."""

    def __init__(self, client: WeatherBaseClient) -> None:
        self.client = client

    def get_weather_data(self) -> WeatherLog:
        """Get weather data."""
        pass
