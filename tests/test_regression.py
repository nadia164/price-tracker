from pathlib import Path

from src.parse import parse_report

KNOWN_GOOD = Path("tests/fixtures/ncr-2026-10-27.pdf")


def test_known_good_report_still_parses_the_same():
    rows = parse_report(KNOWN_GOOD)

    assert len(rows) == 292
    assert len({row["city"] for row in rows}) == 12

    caloocan_petron_ron95 = [
        row for row in rows
        if row["city"] == "Caloocan City"
        and row["product"] == "RON 95"
        and row["brand"] == "PETRON"
    ]
    assert caloocan_petron_ron95 == [{
        "city": "Caloocan City", "product": "RON 95", "brand": "PETRON",
        "price_low": 82.4, "price_high": 88.5,
    }]