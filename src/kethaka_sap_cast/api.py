# C4 forecast service. Run locally with:
# Command: uv run uvicorn kethaka_sap_cast.api:app --reload
# Interactive docs: http://127.0.0.1:8000/docs

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from kethaka_sap_cast import forecast

app = FastAPI(
    title="Kethaka C4 - Sap Yield Forecast",
    description="7-day daily sap forecast for the estate, with replay mode for verification.",
    version="0.1.0",
)


class HistoryDay(BaseModel):
    date: str
    yield_l: float
    tapped: bool


class ForecastDay(BaseModel):
    date: str
    yield_l: float
    lower_l: float
    upper_l: float


class ForecastResponse(BaseModel):
    mode: str
    as_of: str
    model: str
    trained_until: str
    backtest_mape_pct: float
    unit: str
    rain_source: str
    history: list[HistoryDay]
    forecast: list[ForecastDay]

# Liveness check used by the common backend before forwarding requests.
@app.get("/health", tags=["service"])
def health() -> dict:
    return {"status": "ok", "service": "c4-forecast"}


@app.get("/forecast", response_model=ForecastResponse, tags=["forecast"])
def get_forecast(
    horizon_days: int = Query(7, ge=1, le=7, description="Days to forecast (1-7, as validated in the backtest)"),
):
    """Daily sap forecast for the days after the last recorded day."""
    try:
        return forecast.latest_forecast(horizon_days)
    except requests.RequestException as err:
        raise HTTPException(503, f"Weather service unavailable: {err}")
    except ValueError as err:
        raise HTTPException(422, str(err))