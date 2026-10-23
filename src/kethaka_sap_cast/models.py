# Forecasting models. Every model has the same shape:

# model(train, test) -> predictions for each row of test

# train: all days before the forecast cut-off (with sap_l and features)
# test:  the days to forecast (dates, plus weather for weather-based models)
import numpy as np
import pandas as pd
import itertools
import warnings

from statsmodels.tsa.arima.model import ARIMA

TARGET = "sap_l"

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