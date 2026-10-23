# Run every model through the same backtest and save a results table:

#  Command: uv run python -m kethaka_sap_cast.benchmark

import pandas as pd

from kethaka_sap_cast import config, models
from kethaka_sap_cast.evaluation import backtest, score, score_by_days_ahead
from kethaka_sap_cast.features import add_model_columns

MODELS = {
    "Naive (last value)": models.naive,
    "Mean of last 7 days": models.mean_7d,
    "ARIMA (AIC-selected)": models.arima,
}

EXPERIMENTS = config.ROOT / "experiments"


def run() -> pd.DataFrame:
    data = pd.read_csv(config.PROCESSED / "dataset.csv", parse_dates=["date"])
    data = add_model_columns(data)

    summary, by_horizon = [], {}
    for name, model in MODELS.items():
        print(f"Backtesting: {name}")
        results = backtest(data, model, target=models.TARGET)
        summary.append({"model": name, **score(results)})
        by_horizon[name] = score_by_days_ahead(results)

    summary = pd.DataFrame(summary).sort_values("MAPE_%")
    by_horizon = pd.DataFrame(by_horizon)
    by_horizon.index.name = "days_ahead"

    EXPERIMENTS.mkdir(exist_ok=True)
    summary.to_csv(EXPERIMENTS / "benchmark_summary.csv", index=False)
    by_horizon.to_csv(EXPERIMENTS / "benchmark_by_days_ahead.csv")

    print("\n" + summary.to_markdown(index=False))
    print("\nMAPE % by days ahead\n" + by_horizon.to_markdown())
    return summary


if __name__ == "__main__":
    run()