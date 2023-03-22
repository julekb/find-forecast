import abc
import datetime
from typing import Dict, List


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
            self, lon: str, lat: str, target_timestamp: datetime.datetime, params: List[str]
    ) -> Dict:
        """Get forcast data."""
