import pandas as pd

from kethaka_sap_cast.clean import (
    clean_records,
    daily_by_tapper,
    daily_estate,
    fix_decimal_slips,
    name_key,
    parse_date,
)

ALIASES = {"mahinda": "T1", "manju": "T2"}   # small made-up lookup for tests


def test_parse_date_handles_every_format():
    for raw in ["04-Apr-2025", "04.04.2025", "04/04/2025", "2025-04-04", "Apr 04, 2025"]:
        assert parse_date(raw) == pd.Timestamp("2025-04-04"), raw


def test_parse_date_is_day_first():
    assert parse_date("03/06/2025") == pd.Timestamp("2025-06-03")   # 3 June, not 6 March


def test_unreadable_date_becomes_nat():
    assert pd.isna(parse_date("sometime in April"))


def test_name_key_simplifies_spellings():
    assert name_key("Mr. Mahinda ") == "mahinda"
    assert name_key("Sena Pala") == "senapala"
    assert name_key("MANJU.") == "manju"


def test_decimal_slip_is_divided_by_ten():
    volume = pd.Series([21.0, 22.0, 220.0, 23.0])
    tapper = pd.Series(["T2"] * 4)
    fixed, was_fixed = fix_decimal_slips(volume, tapper, factor=3.0)
    assert fixed.tolist() == [21.0, 22.0, 22.0, 23.0]
    assert was_fixed.tolist() == [False, False, True, False]


def _raw(rows):
    """Build a tiny raw table shaped like load_raw() output."""
    df = pd.DataFrame(rows, columns=["date_raw", "name_raw", "value_raw"])
    df.insert(0, "source_row", range(2, len(df) + 2))
    return df


def test_split_collections_summed_and_repeats_dropped():
    raw = _raw([
        ("04/04/2025", "Mr. Mahinda", 7.2),   # split collection, part 1
        ("04.04.2025", "Mahinda", 6.4),       # split collection, part 2
        ("04-Apr-2025", "Manju", 21.3),
        ("04-Apr-2025", "Manju", 21.3),       # typed twice -> dropped
    ])
    records = clean_records(raw, ALIASES, slip_factor=3.0)
    assert records["is_duplicate"].sum() == 1

    by_tapper = daily_by_tapper(records).set_index("tapper")["volume_l"]
    assert by_tapper["T1"] == 13.6
    assert by_tapper["T2"] == 21.3

    estate = daily_estate(daily_by_tapper(records))
    assert estate["total_l"].item() == 34.9