import abc
import pickle as pkl
import os
import errno

from src.domain import Forecast


class BaseRepository(abc.ABC):
    """Base repository class."""


class PklRepository(BaseRepository):
    BASE_DIR: str

    def __init__(self, base_dir="storage/pkl_repo"):
        self.BASE_DIR = base_dir

    def save_forecast(self, forecast: Forecast):
        with open(f"{self.BASE_DIR}/forecast_1.pkl", "wb") as f:  # TODO: generate_ids
            pkl.dump(forecast, f)

    def retrieve_forecast_by_id(self, id: int):
        try:
            with open(f"{self.BASE_DIR}/forecast_{str(id)}.pkl", "rb") as f:
                forecast = pkl.load(f)
        except FileNotFoundError:
            raise
        return forecast
