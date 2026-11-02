from datetime import date

import pytest

from src.extract import parse_week_start


@pytest.mark.parametrize(
    "text, row_year, expected",
    [
        ("October 20 to 26", 2026, date(2026, 10, 20)),
        ("September 29 to October 5", 2026, date(2026, 9, 29)),
        ("February 10-16", 2026, date(2026, 2, 10)),
        ("April 29 to May 05", 2025, date(2025, 4, 29)),
        ("January 4", 2024, date(2024, 1, 4)),
        ("December 30, 2025 to January 5, 2026", 2025, date(2025, 12, 30)),
        ("December 31, 2024 to January 6, 2025", 2025, date(2024, 12, 31)),
    ],
)
def test_parse_week_start(text, row_year, expected):
    assert parse_week_start(text, row_year) == expected


def test_parse_week_start_rejects_text_without_a_date():
    with pytest.raises(ValueError):
        parse_week_start("To be announced", 2026)