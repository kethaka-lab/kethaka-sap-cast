import numpy as np
import pandas as pd

from kethaka_sap_cast.evaluation import backtest, mape, rmse


def test_mape_and_rmse():
    assert mape([100, 200], [110, 180]) == 10.0      # off by 10% and 10%
    assert rmse([10, 10], [13, 7]) == 3.0             # off by 3 L both times


def test_backtest_never_trains_on_the_future():
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=20),
        "total_l": range(20),
        "is_complete": True,
    })
    seen = []

    def spy(train, test):
        seen.append((train["date"].max(), test["date"].min()))
        return np.zeros(len(test))

    backtest(df, spy, initial_days=10, horizon=5)
    assert all(last_train < first_test for last_train, first_test in seen)
    assert len(seen) == 2    # cut-offs at day 10 and day 15