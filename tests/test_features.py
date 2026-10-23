import pandas as pd

from kethaka_sap_cast.features import add_model_columns


def test_incomplete_day_is_interpolated_and_rain_uses_past_only():
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=3),
        "total_l": [60.0, 30.0, 70.0],               # day 2 was not tapped
        "is_complete": [True, False, True],
        "precipitation_sum": [5.0, 10.0, 0.0],
    })
    out = add_model_columns(df)
    assert out["sap_l"].tolist() == [60.0, 65.0, 70.0]     # filled halfway
    assert out["rain_10d"].tolist() == [0.0, 5.0, 15.0]    # rain BEFORE each day