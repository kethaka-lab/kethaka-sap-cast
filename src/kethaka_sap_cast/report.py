# Write reports/data_quality.md: what was wrong in the raw data and what was fixed.
from pathlib import Path

import pandas as pd

# Automatic fixes that were checked against the physical logbook.
VERIFIED = "Verified against the logbook by the farm owner."


def write_report(records: pd.DataFrame, by_tapper: pd.DataFrame, estate: pd.DataFrame, path: Path) -> None:
    summary = pd.DataFrame({
        "item": [
            "Rows in raw file (excluding blank lines)",
            "Rows kept",
            "Duplicate rows dropped",
            "Rows with no volume",
            "Decimal slips fixed",
            "Split collections summed (tapper-days with 2+ entries)",
            "Calendar days",
            "Days with no entries",
        ],
        "value": [
            len(records),
            int(records["kept"].sum()),
            int(records["is_duplicate"].sum()),
            int(records["volume_l"].isna().sum()),
            int(records["fixed_decimal_slip"].sum()),
            int((by_tapper["n_entries"] > 1).sum()),
            len(estate),
            int((estate["n_tappers"] == 0).sum()),
        ],
    })

    slips = records[records["fixed_decimal_slip"]][["source_row", "date", "tapper", "value_raw", "volume_l"]].copy()
    slips["date"] = slips["date"].dt.date

    coverage = by_tapper.groupby("tapper").agg(
        first_day=("date", "min"),
        last_day=("date", "max"),
        days=("date", "nunique"),
        median_l=("volume_l", "median"),
    ).reset_index()
    coverage["first_day"] = coverage["first_day"].dt.date
    coverage["last_day"] = coverage["last_day"].dt.date

    monthly = estate.groupby(estate["date"].dt.to_period("M")).agg(
        mean_total_l=("total_l", "mean"),
        mean_per_tapper_l=("yield_per_tapper_l", "mean"),
        typical_daily_change_l=("total_l", lambda s: s.diff().abs().median()),
    ).round(2).reset_index()

    text = f"""# Data-quality report: farm logbook 2025


## Summary

{summary.to_markdown(index=False)}

## Decimal slips fixed

{VERIFIED}

{slips.to_markdown(index=False)}

## Tapper coverage

{coverage.to_markdown(index=False)}

## Monthly overview

`typical_daily_change_l` is the median day-to-day change in estate total.

{monthly.to_markdown(index=False)}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")