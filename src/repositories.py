import dataclasses
import os
import pickle as pkl
import re

from domain.models import Forecast


class PklRepository:
    #: Storage directory.
    BASE_DIR: str

    def __init__(self, base_dir: str = "storage/pkl_repo"):
        self.BASE_DIR = base_dir

    def _save_forecast(self, forecast: Forecast):
        with open(f"{self.BASE_DIR}/forecast_{forecast.id}.pkl", "wb") as f:
            pkl.dump(forecast, f)
        return forecast

    def save_forecast(self, forecast: Forecast) -> Forecast:
        """
        If an object does not have id value, a new value is set,
        and object is saved to storage and returned a new instance
        of a Forecast class with the newly set identifier.
        """
        if forecast.id:
            raise

        next_id = self._get_last_forecast_id() + 1
        forecast.set_id(next_id)
        return self._save_forecast(forecast)

    def _retrieve_forecast(self, forecast_id: int):
        with open(f"{self.BASE_DIR}/forecast_{str(forecast_id)}.pkl", "rb") as f:
            try:
                forecast = pkl.load(f)
            except FileNotFoundError:
                raise
        return forecast

    def retrieve_forecast(self, forecast_id: int) -> Forecast:
        return self._retrieve_forecast(forecast_id)

    def _get_last_forecast_id(self) -> int:
        """
        Search for all records in the storage and return the identifier
        of with the highest value existing.
        """
        regex = re.compile(r"forecast_[1-9]\d*.pkl$")

        forecast_names = [file for file in os.listdir(self.BASE_DIR) if regex.match(file)]
        if not forecast_names:
            return 0
        forecast_ids = [int(fname[9:-4]) for fname in forecast_names]
        return max(forecast_ids)


@dataclasses.dataclass
class LocationRepository:
    locations_data: dict

    def get_location(self, location_name: str):
        try:
            return self.locations_data[location_name]
        except KeyError:
            raise Exception("Location not found.")
