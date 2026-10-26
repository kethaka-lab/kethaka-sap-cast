# C4 forecast service. Run locally with:
# Command: uv run uvicorn kethaka_sap_cast.api:app --reload
# Interactive docs: http://127.0.0.1:8000/docs

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from kethaka_sap_cast import forecast

from datetime import date

import pandas as pd

from pathlib import Path

from fastapi.responses import FileResponse

app = FastAPI(
    title="Kethaka C4 - Sap Yield Forecast",
    description="7-day daily sap forecast for the estate, with replay mode for verification.",
    version="0.1.0",
)

STATIC = Path(__file__).parent / "static"

class HistoryDay(BaseModel):
    date: str
    yield_l: float
    tapped: bool


class ForecastDay(BaseModel):
    date: str
    yield_l: float
    lower_l: float
    upper_l: float
    actual_l: float | None = None    # replay only
    tapped: bool | None = None       # replay only
    error_pct: float | None = None   # replay only; null on not-tapped days


class ForecastResponse(BaseModel):
    mode: str                         # "latest" or "replay"
    as_of: str
    model: str
    trained_until: str
    backtest_mape_pct: float
    unit: str
    rain_source: str
    replay_mape_pct: float | None = None
    history: list[HistoryDay]
    forecast: list[ForecastDay]

# Liveness check used by the common backend before forwarding requests.
@app.get("/health", tags=["service"])
def health() -> dict:
    return {"status": "ok", "service": "c4-forecast"}

@app.get("/", include_in_schema=False)
def demo_page():
    """Demo page for presenting forecasts and replay verification."""
    return FileResponse(STATIC / "index.html")


# Daily sap forecast.
#     - No `as_of`: forecast the days after the last recorded day (saved model).
#     - With `as_of`: replay. Train only on data up to that date, then compare with what actually happened.
@app.get("/forecast", response_model=ForecastResponse, tags=["forecast"])
def get_forecast(
    horizon_days: int = Query(7, ge=1, le=7, description="Days to forecast (1-7, as validated in the backtest)"),
    as_of: date | None = Query(None, description="Replay: forecast as if it were this date (2025-03-31 to 2025-12-24)"),
):
    
    try:
        if as_of is None:
            return forecast.latest_forecast(horizon_days)
        return forecast.replay_forecast(pd.Timestamp(as_of), horizon_days)
    except requests.RequestException as err:
        raise HTTPException(503, f"Weather service unavailable: {err}")
    except ValueError as err:
        raise HTTPException(422, str(err))