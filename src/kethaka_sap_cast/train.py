# Train the production model on all available data and save it:
# Command: uv run python -m kethaka_sap_cast.train
# Re-run whenever new logbook or sensor data is added.

import json
from datetime import datetime, timezone

import pandas as pd
import prophet
from prophet.serialize import model_to_json

from kethaka_sap_cast import config, models
from kethaka_sap_cast.features import add_model_columns

MODEL_NAME = "Prophet + 10-day rain"
REGRESSORS = ["rain_10d"]


def train() -> dict:
    data = add_model_columns(pd.read_csv(config.PROCESSED / "dataset.csv", parse_dates=["date"]))
    model = models.fit_prophet(data, REGRESSORS)

    # Backtest score for this model, from the latest benchmark run
    summary = pd.read_csv(config.ROOT / "experiments" / "benchmark_summary.csv")
    row = summary[summary["model"] == MODEL_NAME].iloc[0]

    meta = {
        "model": MODEL_NAME,
        "regressors": REGRESSORS,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_from": str(data["date"].min().date()),
        "data_until": str(data["date"].max().date()),
        "training_days": len(data),
        "backtest_mape_pct": float(row["MAPE_%"]),
        "backtest_rmse_l": float(row["RMSE_L"]),
        "prophet_version": prophet.__version__,
    }

    config.ARTIFACTS.mkdir(exist_ok=True)
    config.MODEL_FILE.write_text(model_to_json(model), encoding="utf-8")
    config.MODEL_META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))