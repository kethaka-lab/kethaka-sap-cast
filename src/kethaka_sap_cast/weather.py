# Daily historical weather for the farm from the Open-Meteo archive API.

# Docs: https://open-meteo.com/en/docs/historical-weather-api
# Results are cached as CSV in data/raw/, so the API is called once per date range.

from pathlib import Path

import pandas as pd
import requests

from kethaka_sap_cast import config

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Rain and sunshine affect sap volume and sugar content; temperature and
# evapotranspiration capture heat and water stress on the palm.
DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",          # mm
    "precipitation_hours",
    "sunshine_duration",          # seconds -> converted to hours below
    "et0_fao_evapotranspiration", # mm
]

 # Turn the API's JSON response into a daily table.
def to_frame(payload: dict) -> pd.DataFrame:
    df = pd.DataFrame(payload["daily"]).rename(columns={"time": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["sunshine_hours"] = (df.pop("sunshine_duration") / 3600).round(2)
    return df

# Daily weather between start and end (YYYY-MM-DD), from cache if available.
def fetch_weather(start: str, end: str) -> pd.DataFrame:
    cache = config.RAW / f"weather_{start}_{end}.csv"
    if cache.exists():
        return pd.read_csv(cache, parse_dates=["date"])

    params = {
        "latitude": config.FARM_LAT,
        "longitude": config.FARM_LON,
        "start_date": start,
        "end_date": end,
        "daily": ",".join(DAILY_VARS),
        "timezone": config.TIMEZONE,
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=60)
    response.raise_for_status()           # stop with an error if the API failed
    df = to_frame(response.json())
    df.to_csv(cache, index=False)
    return df