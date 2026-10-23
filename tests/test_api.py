import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from kethaka_sap_cast import config, models
from kethaka_sap_cast.api import app
from kethaka_sap_cast.features import add_model_columns

# Data and model are gitignored, so skip these tests where they don't exist
pytestmark = pytest.mark.skipif(
    not (config.MODEL_FILE.exists() and (config.PROCESSED / "dataset.csv").exists()),
    reason="needs local dataset and trained model (run pipeline and train first)",
)

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_latest_forecast_shape_and_range():
    body = client.get("/forecast").json()
    assert body["mode"] == "latest"
    assert len(body["forecast"]) == 7
    for day in body["forecast"]:
        assert day["lower_l"] <= day["yield_l"] <= day["upper_l"]


def test_same_request_gives_same_answer():
    first = client.get("/forecast", params={"as_of": "2025-11-20"}).json()
    second = client.get("/forecast", params={"as_of": "2025-11-20"}).json()
    assert first == second


def test_replay_trains_only_up_to_as_of():
    body = client.get("/forecast", params={"as_of": "2025-11-20"}).json()
    assert body["trained_until"] == "2025-11-20"
    assert body["history"][-1]["date"] == "2025-11-20"
    assert body["forecast"][0]["date"] == "2025-11-21"
    assert all(day["actual_l"] is not None for day in body["forecast"])

# Replaying the first backtest cut-off must give the backtest's own forecast.
def test_replay_matches_the_benchmark():   
    data = add_model_columns(pd.read_csv(config.PROCESSED / "dataset.csv", parse_dates=["date"]))
    train, test = data.iloc[:90], data.iloc[90:97]
    benchmark = models.prophet_rain(train, test).round(1)

    as_of = train["date"].max().strftime("%Y-%m-%d")
    body = client.get("/forecast", params={"as_of": as_of}).json()
    service = [day["yield_l"] for day in body["forecast"]]
    assert np.allclose(service, benchmark)


@pytest.mark.parametrize("params", [
    {"horizon_days": 10},
    {"as_of": "2025-02-01"},     # too little training data
    {"as_of": "2025-12-28"},     # not enough recorded days after
    {"as_of": "not-a-date"},
])
def test_invalid_requests_are_rejected(params):
    assert client.get("/forecast", params=params).status_code == 422