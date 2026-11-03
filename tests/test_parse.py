import pytest

from src.parse import parse_price_range


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