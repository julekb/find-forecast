from datetime import datetime, timedelta

from src.domain.models import ForecastParams, ForecastModels
from src.domain.functions import get_forecasts

forecast_source_and_models = [
    {"forecast_service_name": "OpenMeteoExternalService", "model_name": ForecastModels.MODEL_ICON},
    {"forecast_service_name": "WindyComExternalService", "model_name": ForecastModels.DEFAULT},
]


def test_get_forecasts(forecast_service, example_location):
    results = get_forecasts(
        service=forecast_service,
        forecast_source_and_models=forecast_source_and_models,
        params=(ForecastParams.TEMPERATURE,),
        location=example_location,
        target_timestamp=datetime.utcnow() - timedelta(days=1),
    )
    assert len(results) == 2
