## -----Project-wide settings: paths and farm location -------
from pathlib import Path

# ---- Paths ------
ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"              # original files, never edited
INTERIM = DATA / "interim"      # cleaned row-level records
PROCESSED = DATA / "processed"  # daily tables used for modelling
REPORTS = ROOT / "reports"

# The farm logbook transcription (Apr-Dec 2025)
FARM_RECORDS_FILE = RAW / "thelijja_2025_full.xlsx"

# Tapper name spellings and aliases (for cleaning the logbook)
TAPPER_ALIASES_FILE = RAW / "tapper_aliases.json"

# Trained model files
ARTIFACTS = ROOT / "artifacts"
MODEL_FILE = ARTIFACTS / "prophet_rain.json"
MODEL_META_FILE = ARTIFACTS / "prophet_rain.meta.json"

# ---- Farm location (used for the Open-Meteo weather download) ---------
FARM_LAT = 6.362
FARM_LON = 80.3518
TIMEZONE = "Asia/Colombo"

# A reading more than this many times the tapper's median is treated as a
# misplaced decimal point (e.g. 140 typed for 14.0) and divided by 10.
DECIMAL_SLIP_FACTOR = 3.0