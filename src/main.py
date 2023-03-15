import os

from adapters.windycom.client import WindyComClient
from services import WindyComService


if __name__ == '__main__':

    service = WindyComService(
        client=WindyComClient(
        user=os.environ["METEOMATICS_USER"],
        password=os.environ["METEOMATICS_PASSWORD"]
        )
    )




