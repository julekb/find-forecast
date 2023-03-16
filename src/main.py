import os

from src.adapters.windycom.client import WindyComClient
from src.services import WindyComExternalService


if __name__ == '__main__':

    service = WindyComExternalService(
        client=WindyComClient(
        user=os.environ["METEOMATICS_USER"],
        password=os.environ["METEOMATICS_PASSWORD"]
        )
    )




