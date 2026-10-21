## Load the farm logbook transcription exactly as typed - no cleaning data.

# Output columns:
#     source_row  row number in the spreadsheet (header = row 1), so every
#                 cleaned value can be traced back to the original entry
#     date_raw    the date cell as typed (a datetime, or text like "04.04.2025")
#     name_raw    the tapper name as typed
#     value_raw   the sap volume as typed (a number, or text like "13.8 l")

from pathlib import Path

import pandas as pd

COLUMNS = ["date_raw", "name_raw", "value_raw"]


def load_raw(path: Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".xlsx":
        # dtype=object: keep every cell exactly as typed. Without it, pandas
        # guesses types and could silently convert or drop odd values.
        df = pd.read_excel(path, dtype=object)
    elif path.suffix == ".csv":
        df = pd.read_csv(path, dtype=str)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    df = df.iloc[:, :3].copy()   # first 3 columns: date, name, volume
    df.columns = COLUMNS         # our own names, so stray spaces don't matter
    df.insert(0, "source_row", range(2, len(df) + 2))
    return df