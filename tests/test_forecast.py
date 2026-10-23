import numpy as np
import pandas as pd
import pytest

from kethaka_sap_cast.forecast import rain_10d_for


def test_rain_10d_sums_the_previous_ten_days():
    rain = pd.Series(1.0, index=pd.date_range("2025-01-01", periods=20))
    dates = pd.date_range("2025-01-15", periods=3)
    assert rain_10d_for(dates, rain).tolist() == [10.0, 10.0, 10.0]


def test_rain_10d_can_reach_one_day_past_the_known_rain():
    # Forecasting 21 Jan only needs rain up to 20 Jan
    rain = pd.Series(2.0, index=pd.date_range("2025-01-01", periods=20))
    dates = pd.DatetimeIndex(["2025-01-21"])
    assert rain_10d_for(dates, rain).tolist() == [20.0]


def test_rain_10d_refuses_to_undercount():
    rain = pd.Series(1.0, index=pd.date_range("2025-01-01", periods=20))
    rain = rain.drop(pd.Timestamp("2025-01-12"))           # one day missing
    with pytest.raises(ValueError, match="Rainfall missing"):
        rain_10d_for(pd.DatetimeIndex(["2025-01-15"]), rain)