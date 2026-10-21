# Rebuild every cleaned table from the raw logbook with one command:
# Command to run the data cleaning pipeline: uv run python -m kethaka_sap_cast.pipeline

from kethaka_sap_cast import config
from kethaka_sap_cast.clean import clean_records, daily_by_tapper, daily_estate, load_aliases
from kethaka_sap_cast.farm_records import load_raw


def run() -> None:
    config.INTERIM.mkdir(parents=True, exist_ok=True)
    config.PROCESSED.mkdir(parents=True, exist_ok=True)

    print("1/3 Loading logbook")
    raw = load_raw(config.FARM_RECORDS_FILE)
    aliases = load_aliases(config.TAPPER_ALIASES_FILE)

    print("2/3 Cleaning")
    records = clean_records(raw, aliases, config.DECIMAL_SLIP_FACTOR)
    by_tapper = daily_by_tapper(records)
    estate = daily_estate(by_tapper)

    print("3/3 Saving")
    records.to_csv(config.INTERIM / "records_clean.csv", index=False)
    by_tapper.to_csv(config.PROCESSED / "daily_by_tapper.csv", index=False)
    estate.to_csv(config.PROCESSED / "daily_estate.csv", index=False)

    print(f"Done: {records['kept'].sum()}/{len(records)} entries kept, "
          f"{len(estate)} days, {estate['date'].min().date()} to {estate['date'].max().date()}")


if __name__ == "__main__":
    run()