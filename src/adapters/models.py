import abc
import datetime
from typing import Dict, List


from src.dtos import ForecastDTO


class ForecastBaseClient(abc.ABC):
    """Abstract base client class."""
    def __init__(self, config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_service__(**config)

    @abc.abstractmethod
    def __init_service__(self, *args, **kwargs):
        """Initialize service-specific entities."""

    @abc.abstractmethod
    def get_forecast_data(
            self, target_timestamp: datetime.datetime, extra_params: str, lon: str, lat: str, wind_params: List
    ) -> ForecastDTO:
        """Get forcast data."""
