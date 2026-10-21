# Kethaka C4: Kithul Sap Yield Forecasting

Component 4 of Kethaka (J26-SE-337). Forecasts daily Kithul sap yield (litres)
from farm logbook records and weather, benchmarking multiple forecasting models.

## Data
- **Farm logbook, 2025**: daily sap collected per tapper, hand-recorded and
  transcribed. Tappers are anonymised as T1-T4. Not committed (`data/` is gitignored).
- **Weather**: Open-Meteo Historical Weather Archive for the farm location.

## Setup
```bash
uv sync
```
Place the logbook at `data/raw/thelijja_2025_full.xlsx` and the name mapping at
`data/raw/tapper_aliases.json`.

## Run
```bash
uv run python -m kethaka_sap_cast.pipeline   # rebuild all data tables
uv run pytest                                # run tests
```

| Output | Contents |
|---|---|
| `data/interim/records_clean.csv` | Every logbook entry with cleaning flags |
| `data/processed/daily_by_tapper.csv` | Sap per tapper per day |
| `data/processed/daily_estate.csv` | Estate total per day |
| `data/processed/dataset.csv` | Daily sap plus weather (model input) |
| `reports/data_quality.md` | What was fixed and verified |

## Cleaning rules
1. Dates: five text formats plus Excel dates, read day-first.
2. Names: spelling variants mapped to anonymous IDs.
3. Volumes: values over 3x a tapper's median divided by 10 (decimal slip).
   All fixes verified against the logbook.
4. Duplicates: identical repeats dropped; different values on the same day
   are split collections and summed.