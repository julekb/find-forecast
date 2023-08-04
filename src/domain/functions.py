from datetime import datetime
from typing import Iterable

from src.domain.models import Forecast, Location, ForecastParams, ForecastAnalyzer
from src.services.forecast_services import ForecastService


def get_forecasts(
    service, forecast_source_and_models, params, location, target_timestamp
) -> list[Forecast]:
    forecasts = []
    for source_model in forecast_source_and_models:
        external_service = service.get_external_service(source_model["forecast_service_name"])
        forecasts.append(
            external_service.get_forecast(
                location=location,
                target_timestamp=target_timestamp,
                extra_params=params,
                model=source_model["model_name"],
            )
        )
    return forecasts


def construct_forecast_analyser(
    service: ForecastService,
    forecast_source_and_models: list[dict],
    params: Iterable[ForecastParams | str],
    location: Location,
    target_timestamp: datetime,
) -> ForecastAnalyzer:
    forecasts = get_forecasts(
        service=service,
        forecast_source_and_models=forecast_source_and_models,
        params=params,
        location=location,
        target_timestamp=target_timestamp,
    )
    return ForecastAnalyzer(forecasts=forecasts)
