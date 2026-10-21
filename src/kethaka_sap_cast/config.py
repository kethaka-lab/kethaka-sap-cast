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
FARM_RECORDS_FILE = RAW / "thelijja_2025.xlsx"

# ---- Farm location (used for the Open-Meteo weather download) ---------
FARM_LAT = 6.362
FARM_LON = 80.3518
TIMEZONE = "Asia/Colombo"