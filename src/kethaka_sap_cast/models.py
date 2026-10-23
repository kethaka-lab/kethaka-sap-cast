# Forecasting models. Every model has the same shape:

# model(train, test) -> predictions for each row of test

# train: all days before the forecast cut-off (with sap_l and features)
# test:  the days to forecast (dates, plus weather for weather-based models)
import numpy as np
import pandas as pd
import itertools
import warnings

from statsmodels.tsa.arima.model import ARIMA
import logging

from prophet import Prophet

TARGET = "sap_l"

logging.getLogger("cmdstanpy").disabled = True        # Prophet's optimiser is very chatty
logging.getLogger("prophet").setLevel(logging.ERROR)

# Every future day = the last known day.
def naive(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    return np.repeat(train[TARGET].iloc[-1], len(test))

# Every future day = the average of the last 7 days. (FPP3, section 5.2)
def mean_7d(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    return np.repeat(train[TARGET].iloc[-7:].mean(), len(test))

# ARIMA(p,1,q) with drift. p and q (0-2) are chosen by lowest AIC on the
# training data only, refitted in every backtest fold.
def arima(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    best = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # statsmodels warns on some fits; AIC still valid
        for p, q in itertools.product([0, 1, 2], [0, 1, 2]):
            try:
                fit = ARIMA(train[TARGET].values, order=(p, 1, q), trend="t").fit()
            except Exception:
                continue                  # skip orders that fail to fit
            if best is None or fit.aic < best.aic:
                best = fit
    return best.forecast(len(test))

# Prophet: piecewise-linear trend + effect of regressors.
def _prophet(train: pd.DataFrame, test: pd.DataFrame, regressors: list[str]) -> np.ndarray:
    model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    for name in regressors:
        model.add_regressor(name)
    history = train[["date", TARGET, *regressors]].rename(columns={"date": "ds", TARGET: "y"})
    model.fit(history)
    future = test[["date", *regressors]].rename(columns={"date": "ds"})
    return model.predict(future)["yhat"].values

# Prophet without weather.
def prophet(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    return _prophet(train, test, regressors=[])

# Prophet with rain over the previous 10 days as an input.
def prophet_rain(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    return _prophet(train, test, regressors=["rain_10d"])