import abc
import pickle as pkl
import os
import re

from src.domain import Forecast


class BaseRepository(abc.ABC):
    """Base repository class."""


class PklRepository(BaseRepository):
    #: Storage directory.
    BASE_DIR: str

    def __init__(self, base_dir: str = "storage/pkl_repo"):
        self.BASE_DIR = base_dir

    def save_forecast(self, forecast: Forecast) -> Forecast:
        """
        If an object does not have id value, a new value is set,
        and object is saved to storage and returned a new instance
        of a Forecast class with the newly set identifier.

        :param forecast: The Forecast object without id.
        :return: The Forecast object with id.
        """
        if forecast.id:
            raise
        next_id = self._get_last_forecast_id() + 1
        forecast.set_id(next_id)
        with open(f"{self.BASE_DIR}/forecast_1.pkl", "wb") as f:  # TODO: generate_ids
            pkl.dump(forecast, f)
        return forecast

    def retrieve_forecast_by_id(self, id: int) -> Forecast:
        """
        Get a Forecast object by identifier.

        :param id: The Forecast identifier.
        :return: The Forecast object.
        """
        try:
            with open(f"{self.BASE_DIR}/forecast_{str(id)}.pkl", "rb") as f:
                forecast = pkl.load(f)
        except FileNotFoundError:
            raise
        return forecast

    def _get_last_forecast_id(self) -> int:
        """
        Search for all records in the storage and return the identifier
        of with the highest value existing.

        :return: Highest Forecast identifier.
        """
        regex = re.compile(r"forecast_[1-9]\d*.pkl$")

        fnames = [file for file in os.listdir(self.BASE_DIR) if regex.match(file)]
        if not fnames:
            return 0
        fids = [int(fname[9:-4]) for fname in fnames]
        return max(fids)
