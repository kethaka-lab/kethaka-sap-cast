# Rolling-origin backtest: score any forecasting model the same, fair way.
from collections.abc import Callable

import numpy as np
import pandas as pd

# A model is any function: (history so far, the days to forecast) -> predictions
Model = Callable[[pd.DataFrame, pd.DataFrame], np.ndarray]


# Train on everything before a cut-off, forecast the next `horizon` days,
# move the cut-off forward by `horizon`, repeat until the data runs out.
# Returns one row per forecast day: the actual value, the prediction,
# how many days ahead it was, and whether the day counts for scoring.
    
def backtest(df: pd.DataFrame, model: Model, target: str = "total_l",
             initial_days: int = 90, horizon: int = 7) -> pd.DataFrame:
    
    rows = []
    for cut in range(initial_days, len(df), horizon):
        train = df.iloc[:cut]
        test = df.iloc[cut:cut + horizon]
        preds = model(train, test)
        rows.append(pd.DataFrame({
            "date": test["date"].values,
            "cutoff": df["date"].iloc[cut - 1],
            "days_ahead": range(1, len(test) + 1),
            "actual": test[target].values,
            "predicted": np.asarray(preds, dtype=float),
            "scored": test["is_complete"].values,
        }))
    return pd.concat(rows, ignore_index=True)


# Mean absolute percentage error: average % the forecast is off by.
def mape(actual, predicted) -> float:
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    return float(np.mean(np.abs((actual - predicted) / actual)) * 100)

# Root mean squared error, in litres. Punishes big misses more than MAPE.
def rmse(actual, predicted) -> float:
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))

# MAPE and RMSE over scored (complete) days only.
def score(results: pd.DataFrame) -> dict:
    s = results[results["scored"]]
    return {
        "MAPE_%": round(mape(s["actual"], s["predicted"]), 2),
        "RMSE_L": round(rmse(s["actual"], s["predicted"]), 2),
        "days_scored": len(s),
    }

# MAPE for 1, 2, ... 7 days ahead. Error should grow the further out you go.
def score_by_days_ahead(results: pd.DataFrame) -> pd.Series:
    s = results[results["scored"]]
    return s.groupby("days_ahead").apply(lambda g: round(mape(g["actual"], g["predicted"]), 2))