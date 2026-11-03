import pytest

from src.parse import IncompletePriceError, normalize_column_name, parse_price_range, is_extra_report_table


def test_parse_price_range_normal():
    assert parse_price_range("82.40 88.50") == (82.4, 88.5)


def test_parse_price_range_same_low_and_high():
    assert parse_price_range("95.10 95.10") == (95.1, 95.1)


def test_parse_price_range_extra_spaces():
    assert parse_price_range("  82.40   88.50  ") == (82.4, 88.5)


@pytest.mark.parametrize("cell", ["", None, "   "])
def test_parse_price_range_empty_cell_returns_none(cell):
    assert parse_price_range(cell) is None


@pytest.mark.parametrize("cell", ["82.40", "82.40 88.50 90.00"])
def test_parse_price_range_wrong_number_of_prices(cell):
    with pytest.raises(ValueError):
        parse_price_range(cell)


def test_parse_price_range_low_above_high():
    with pytest.raises(ValueError):
        parse_price_range("90.00 80.00")


def test_parse_price_range_not_a_number():
    with pytest.raises(ValueError):
        parse_price_range("#N/A 88.50")

@pytest.mark.parametrize("cell", ["NO LFRO", "  NO   LFRO ", "0.00 0.00"])
def test_parse_price_range_no_price_markers_return_none(cell):
    assert parse_price_range(cell) is None


@pytest.mark.parametrize("cell", ["78.00 0.00", "0.00 72.53"])
def test_parse_price_range_one_missing_price_raises_incomplete(cell):
    with pytest.raises(IncompletePriceError):
        parse_price_range(cell)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("PETRON", "PETRON"),
        ("FLYING V", "FLYING V"),
        ("INDEPENDENT OVERALL RANGE", "INDEPENDENT"),
        ("INDEPENDENT\nOVERALL RANGE", "INDEPENDENT"),
        ("  FLYING   V ", "FLYING V"),
    ],
)
def test_normalize_column_name(raw, expected):
    assert normalize_column_name(raw) == expected

def test_is_extra_report_table_detects_prevailing_prices_page():
    table = [
        ["PREVAILING RETAIL PRICES OF PETROLEUM PRODUCTS NCR", None, None, None],
        ["(for the week of March 17-23, 2026)", None, None, None],
    ]
    assert is_extra_report_table(table) is True


def test_is_extra_report_table_ignores_normal_price_table():
    table = [
        ["", "PETRON", "SHELL", "CALTEX", None],
        ["PRODUCT", "", "", "", None],
        ["RON 100", "82.40 88.50", "", "", ""],
    ]
    assert is_extra_report_table(table) is False