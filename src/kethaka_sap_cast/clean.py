##Cleaning rules for the farm logbook. Each rule is a small function so it can be tested on its own.
from datetime import datetime

import pandas as pd
import json
import re
from pathlib import Path

# Text date formats found in the logbook transcription.
# Day comes first (Sri Lankan convention): 04/04/2025 = 4 April.
TEXT_DATE_FORMATS = [
    "%d-%b-%Y",   # 04-Apr-2025
    "%d.%m.%Y",   # 04.04.2025
    "%d/%m/%Y",   # 04/04/2025
    "%Y-%m-%d",   # 2025-04-04
    "%b %d, %Y",  # Apr 04, 2025
]


def parse_date(value) -> pd.Timestamp:
    """Turn one date cell into a Timestamp, or NaT if it can't be read."""
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, datetime):          # already a real date
        return pd.Timestamp(value).normalize()
    text = str(value).strip()
    for fmt in TEXT_DATE_FORMATS:            # try each format in turn
        try:
            return pd.Timestamp(datetime.strptime(text, fmt))
        except ValueError:
            continue
    return pd.NaT                            # nothing matched

# Simplify a typed name: 'Mr. Mahinda ' -> 'mahinda', 'Sena Pala' -> 'senapala'.
def name_key(name: str) -> str:
    key = str(name).strip().lower()
    key = re.sub(r"^mr\.?\s*", "", key)   # remove a leading "mr" or "mr."
    key = re.sub(r"[\s.]", "", key)       # remove spaces and dots
    return key

# Read the alias file and flip it into a lookup: {'mahindha': 'T1', ...}.
def load_aliases(path: Path) -> dict[str, str]:
    groups = json.loads(Path(path).read_text())
    return {alias: tapper_id for tapper_id, aliases in groups.items() for alias in aliases}

# Anonymous tapper ID for a typed name, or None if the spelling is unknown.
def normalise_name(name, aliases: dict[str, str]) -> str | None:
    if pd.isna(name):
        return None
    return aliases.get(name_key(name))

# Volume cells -> float litres. Anything non-numeric becomes NaN.
def to_volume(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce")

# Divide by 10 any reading more than `factor` x that tapper's median.
# Returns (fixed_volume, was_fixed) so every change can be reported.
def fix_decimal_slips(volume: pd.Series, tapper: pd.Series, factor: float) -> tuple[pd.Series, pd.Series]:
    median = volume.groupby(tapper).transform("median")
    was_fixed = volume > factor * median
    fixed = volume.where(~was_fixed, volume / 10)
    return fixed, was_fixed