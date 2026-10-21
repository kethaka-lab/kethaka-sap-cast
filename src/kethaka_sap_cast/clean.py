##Cleaning rules for the farm logbook. Each rule is a small function so it can be tested on its own.
from datetime import datetime

import pandas as pd

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