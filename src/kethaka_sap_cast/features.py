# Prepare the daily dataset for modelling.
import pandas as pd

RAIN_WINDOW_DAYS = 10   # from EDA: sap-rain correlation peaks at 9-10 days


# Add the training target and weather features.

#     sap_l    - total_l, with incomplete days (tapper present, did not tap)
#                replaced by linear interpolation between neighbouring complete
#                days. Models train on this; scoring still skips those days.
#     rain_10d - total rain over the previous 10 days (not including today).
    
def add_model_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().set_index("date")
    out["sap_l"] = out["total_l"].where(out["is_complete"]).interpolate(method="time")
    out["rain_10d"] = (
        out["precipitation_sum"].rolling(RAIN_WINDOW_DAYS, min_periods=1).sum().shift(1)
    )
    out["rain_10d"] = out["rain_10d"].fillna(0)   # 1 Jan has no previous days
    return out.reset_index()