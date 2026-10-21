# Rebuild every cleaned table from the raw logbook with one command:
# Command to run the data cleaning pipeline: uv run python -m kethaka_sap_cast.pipeline

from kethaka_sap_cast import config
from kethaka_sap_cast.clean import clean_records, daily_by_tapper, daily_estate, load_aliases
from kethaka_sap_cast.farm_records import load_raw
from kethaka_sap_cast.weather import fetch_weather


def run() -> None:
    config.INTERIM.mkdir(parents=True, exist_ok=True)
    config.PROCESSED.mkdir(parents=True, exist_ok=True)

    print("1/4 Loading logbook")
    raw = load_raw(config.FARM_RECORDS_FILE)
    aliases = load_aliases(config.TAPPER_ALIASES_FILE)

    print("2/4 Cleaning")
    records = clean_records(raw, aliases, config.DECIMAL_SLIP_FACTOR)
    by_tapper = daily_by_tapper(records)
    estate = daily_estate(by_tapper)

    print("3/4 Weather")
    start = estate["date"].min().strftime("%Y-%m-%d")
    end = estate["date"].max().strftime("%Y-%m-%d")
    weather = fetch_weather(start, end)

    print("4/4 Saving")
    dataset = estate.merge(weather, on="date", how="left")
    records.to_csv(config.INTERIM / "records_clean.csv", index=False)
    by_tapper.to_csv(config.PROCESSED / "daily_by_tapper.csv", index=False)
    estate.to_csv(config.PROCESSED / "daily_estate.csv", index=False)
    dataset.to_csv(config.PROCESSED / "dataset.csv", index=False)

    print(f"Done: {records['kept'].sum()}/{len(records)} entries kept, "
          f"{len(dataset)} days x {dataset.shape[1]} columns, "
          f"{start} to {end}")


if __name__ == "__main__":
    run()