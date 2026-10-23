import json
from functools import lru_cache

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_from_json

from kethaka_sap_cast import config
from kethaka_sap_cast.features import RAIN_WINDOW_DAYS, add_model_columns
from kethaka_sap_cast.weather import fetch_weather

RANDOM_SEED = 42    # Prophet samples to build the low-high range; a fixed seed makes it repeatable
HISTORY_DAYS = 14   # recent actual days returned alongside the forecast


@lru_cache
def load_model() -> tuple[Prophet, dict]:
    # Load the saved model and its metadata once, then reuse them.
    model = model_from_json(config.MODEL_FILE.read_text(encoding="utf-8"))
    meta = json.loads(config.MODEL_META_FILE.read_text(encoding="utf-8"))
    return model, meta


@lru_cache
def load_history() -> pd.DataFrame:
    # The full daily dataset with model columns, loaded once.
    return add_model_columns(pd.read_csv(config.PROCESSED / "dataset.csv", parse_dates=["date"]))


# Rain over the 10 days before each date. Same definition as features.py.

    # `rain` is daily rainfall indexed by date. Raises an error if any day
    # needed for the calculation is missing, rather than under-counting.
def rain_10d_for(dates: pd.DatetimeIndex, rain: pd.Series) -> np.ndarray:
    days = pd.date_range(rain.index.min(), dates.max(), freq="D")
    rain = rain.reindex(days)
    needed = pd.date_range(dates.min() - pd.Timedelta(days=RAIN_WINDOW_DAYS),
                           dates.max() - pd.Timedelta(days=1))
    missing = rain.reindex(needed).isna()
    if missing.any():
        raise ValueError(f"Rainfall missing for {list(missing[missing].index.date)}")
    return rain.rolling(RAIN_WINDOW_DAYS, min_periods=1).sum().shift(1).reindex(dates).values


# Forecast each date: expected litres plus an 80% range.
def predict(model: Prophet, dates: pd.DatetimeIndex, rain: pd.Series) -> pd.DataFrame:
    future = pd.DataFrame({"ds": dates, "rain_10d": rain_10d_for(dates, rain)})
    np.random.seed(RANDOM_SEED)
    p = model.predict(future)
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "yield_l": p["yhat"].round(1).values,
        "lower_l": p["yhat_lower"].round(1).values,
        "upper_l": p["yhat_upper"].round(1).values,
    })


def _history_records(history: pd.DataFrame) -> list[dict]:
    recent = history.tail(HISTORY_DAYS)
    return [
        {"date": d.strftime("%Y-%m-%d"), "yield_l": float(v), "tapped": bool(c)}
        for d, v, c in zip(recent["date"], recent["total_l"], recent["is_complete"])
    ]

# Option A: forecast the days after the last recorded day, using the saved model.
def latest_forecast(horizon_days: int) -> dict:
    model, meta = load_model()
    history = load_history()
    last_day = history["date"].max()
    dates = pd.date_range(last_day + pd.Timedelta(days=1), periods=horizon_days, freq="D")

    weather = fetch_weather(dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d"))
    rain = pd.concat([
        history.set_index("date")["precipitation_sum"],
        weather.set_index("date")["precipitation_sum"],
    ])

    return {
        "mode": "latest",
        "as_of": last_day.strftime("%Y-%m-%d"),
        "model": meta["model"],
        "trained_until": meta["data_until"],
        "backtest_mape_pct": meta["backtest_mape_pct"],
        "unit": "litres",
        "rain_source": "observed (Open-Meteo archive)",
        "history": _history_records(history),
        "forecast": predict(model, dates, rain).to_dict(orient="records"),
    }