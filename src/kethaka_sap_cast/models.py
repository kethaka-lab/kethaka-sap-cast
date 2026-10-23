# Forecasting models. Every model has the same shape:

# model(train, test) -> predictions for each row of test

# train: all days before the forecast cut-off (with sap_l and features)
# test:  the days to forecast (dates, plus weather for weather-based models)
import numpy as np
import pandas as pd

TARGET = "sap_l"

# Every future day = the last known day.
def naive(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    return np.repeat(train[TARGET].iloc[-1], len(test))

# Every future day = the average of the last 7 days. (FPP3, section 5.2)
def mean_7d(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    return np.repeat(train[TARGET].iloc[-7:].mean(), len(test))