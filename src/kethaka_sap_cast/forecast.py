import json
from functools import lru_cache

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_from_json

from kethaka_sap_cast import config
from kethaka_sap_cast.features import RAIN_WINDOW_DAYS, add_model_columns
from kethaka_sap_cast.weather import fetch_weather
from kethaka_sap_cast.models import fit_prophet

RANDOM_SEED = 42    # Prophet samples to build the low-high range; a fixed seed makes it repeatable
HISTORY_DAYS = 14   # recent actual days returned alongside the forecast
MIN_TRAINING_DAYS = 90   # same as the backtest's first training window


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

# Earliest and latest allowed as_of dates for replay.
def replay_window(horizon_days: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    history = load_history()
    earliest = history["date"].min() + pd.Timedelta(days=MIN_TRAINING_DAYS - 1)
    latest = history["date"].max() - pd.Timedelta(days=horizon_days)
    return earliest, latest

# Option B: pretend it is `as_of`, train only on data up to that day,
# forecast the next days, and return them next to what actually happened.
def replay_forecast(as_of: pd.Timestamp, horizon_days: int) -> dict:
    earliest, latest = replay_window(horizon_days)
    if not earliest <= as_of <= latest:
        raise ValueError(
            f"as_of must be between {earliest.date()} and {latest.date()} "
            f"({MIN_TRAINING_DAYS}+ days of training, {horizon_days} recorded days after)"
        )

    history = load_history()
    train = history[history["date"] <= as_of]       # nothing after as_of is seen
    model = fit_prophet(train, ["rain_10d"])

    dates = pd.date_range(as_of + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    rain = history.set_index("date")["precipitation_sum"]
    result = predict(model, dates, rain)

    actual = history.set_index("date").loc[dates]
    result["actual_l"] = actual["total_l"].values
    result["tapped"] = actual["is_complete"].values
    result["error_pct"] = ((result["yield_l"] - result["actual_l"]).abs() / result["actual_l"] * 100).round(1)
    result.loc[~result["tapped"], "error_pct"] = None   # not-tapped days are not scored

    scored = result[result["tapped"]]
    week_mape = round(float(scored["error_pct"].mean()), 2) if len(scored) else None

    return {
        "mode": "replay",
        "as_of": as_of.strftime("%Y-%m-%d"),
        "model": "Prophet + 10-day rain",
        "trained_until": as_of.strftime("%Y-%m-%d"),
        "backtest_mape_pct": load_model()[1]["backtest_mape_pct"],
        "unit": "litres",
        "rain_source": "observed (Open-Meteo archive)",
        "replay_mape_pct": week_mape,
        "history": _history_records(train),
        "forecast": result.to_dict(orient="records"),
    }