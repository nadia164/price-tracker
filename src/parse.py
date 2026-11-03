from collections import Counter
from pathlib import Path
import re

import pdfplumber
from src.extract import parse_week_start
import logging

logger = logging.getLogger(__name__)

TABLE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "text"}
HEADER_SEARCH_ROWS = 4
FIRST_PRODUCT = "RON 100"
PRODUCT_WORDS = {"RON", "DIESEL", "KEROSENE"}
FOOTER_START = "Date of"
NO_PRICE_MARKERS = {"NO LFRO"}
CITY_NAME_FIXES = {"Taguig Cty": "Taguig City"}
EXPECTED_BRANDS = [
    "PETRON", "SHELL", "CALTEX", "PHOENIX", "TOTAL",
    "FLYING V", "UNIOIL", "SEAOIL", "PTT", "INDEPENDENT",
]
TITLE_PATTERN = r"For the week of (.+?)\)"
EXTRA_REPORT_MARKERS = ("PREVAILING RETAIL PRICES",)

class IncompletePriceError(ValueError):
    """A price cell where only one of the two prices is filled in."""


def normalize_column_name(name):
    """Clean up a header name, e.g. 'INDEPENDENT OVERALL RANGE' -> 'INDEPENDENT'."""
    name = " ".join(name.split())
    if name.startswith("INDEPENDENT"):
        return "INDEPENDENT"
    return name


def get_column_positions(table):
    """Find each column's name in the first few rows. Return {name: column index}."""
    positions = {}
    for index in range(len(table[0])):
        for row in table[:HEADER_SEARCH_ROWS]:
            value = (row[index] or "").strip()
            if value:
                name = normalize_column_name(value)
                if name not in positions:
                    positions[name] = index
                break

    required = ["PRODUCT"] + EXPECTED_BRANDS
    missing = [name for name in required if name not in positions]
    if missing:
        raise ValueError(f"Missing columns {missing}; found {list(positions)}")
    return positions


def find_product_column_left_edge(page):
    """Return the x position where the product labels (RON, DIESEL...) start."""
    product_x = [word["x0"] for word in page.extract_words()
                 if word["text"] in PRODUCT_WORDS]
    if not product_x:
        raise ValueError(f"Page {page.page_number}: no product labels found")
    return min(product_x)


def read_city_names(page):
    """Return the city names in the AREA column, top to bottom."""
    product_left = find_product_column_left_edge(page)
    words = [word for word in page.extract_words(use_text_flow=True)
             if word["x1"] < product_left]

    lines = []
    for word in words:
        if lines and abs(word["top"] - lines[-1]["top"]) < 1:
            lines[-1]["text"] += " " + word["text"]
        else:
            lines.append({"text": word["text"], "top": word["top"]})

    lines.sort(key=lambda line: line["top"])

    names = []
    for line in lines:
        if line["text"] == "AREA":
            continue
        if line["text"].startswith(FOOTER_START):
            break
        names.append(CITY_NAME_FIXES.get(line["text"], line["text"]))
    return names


def parse_price_range(cell):
    """Turn '82.40 88.50' into (82.4, 88.5). Return None when there's no price."""
    text = " ".join((cell or "").split())
    if not text or text in NO_PRICE_MARKERS:
        return None

    parts = text.split()
    if len(parts) != 2:
        raise ValueError(f"Unexpected price cell: {cell!r}")

    low, high = float(parts[0]), float(parts[1])
    if low == 0 and high == 0:
        return None
    if low == 0 or high == 0:
        raise IncompletePriceError(f"Only one price filled in: {cell!r}")
    if low > high:
        raise ValueError(f"Low price is above high price: {cell!r}")
    return low, high


def parse_page(page, seen_cities, carry_city=None):
    """Return (price rows, new city names, last city) for one page of a report.

    carry_city is the city still open at the end of the previous page: rows at
    the top of this page that come before any RON 100 belong to it.
    """
    table = page.extract_table(TABLE_SETTINGS)
    if not table:
        raise ValueError(f"No table found on page {page.page_number}")

    if is_extra_report_table(table):
        logger.info("Page %d: skipping prevailing-prices summary page", page.page_number)
        return [], [], carry_city

    columns = get_column_positions(table)
    product_column = columns["PRODUCT"]
    cities = [name for name in read_city_names(page) if name not in seen_cities]

    rows = []
    city_index = -1
    current_city = carry_city
    for row in table:
        product = (row[product_column] or "").strip()
        if product in ("", "PRODUCT"):
            continue

        if product == FIRST_PRODUCT:
            city_index += 1
            if city_index >= len(cities):
                raise ValueError(
                    f"Page {page.page_number}: more city blocks than city names {cities}"
                )
            current_city = cities[city_index]

        if current_city is None:
            raise ValueError(
                f"Page {page.page_number}: {product!r} appears before any city"
            )

        for brand in EXPECTED_BRANDS:
            try:
                price = parse_price_range(row[columns[brand]])
            except IncompletePriceError as error:
                logger.warning("Page %d, %s, %s, %s: dropped price (%s)",
                               page.page_number, current_city, product, brand, error)
                continue
            if price is None:
                continue
            rows.append({
                "city": current_city,
                "product": product,
                "brand": brand,
                "price_low": price[0],
                "price_high": price[1],
            })

    blocks = city_index + 1
    if blocks != len(cities):
        raise ValueError(
            f"Page {page.page_number}: {blocks} city blocks but "
            f"{len(cities)} city names {cities}"
        )
    return rows, cities, current_city

def is_extra_report_table(table):
    """Return True if a table's top rows show it's a known non-monitoring report."""
    top_text = " ".join(cell or "" for row in table[:3] for cell in row).upper()
    return any(marker in top_text for marker in EXTRA_REPORT_MARKERS)


def parse_report(pdf_path):
    """Return every price row in one weekly report PDF."""
    all_rows = []
    seen_cities = set()
    current_city = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            rows, cities, current_city = parse_page(page, seen_cities, current_city)
            all_rows.extend(rows)
            seen_cities.update(cities)

    if not all_rows:
        raise ValueError(f"No price rows found in {pdf_path.name}")
    return all_rows

def read_title_week_start(pdf_path):
    """Return the week start date written in the PDF's own title."""
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text() or ""

    match = re.search(TITLE_PATTERN, text)
    if match is None:
        raise ValueError(f"No 'For the week of' title in {pdf_path.name}")

    period = match.group(1)                 # e.g. "October 27 - November 2, 2026"
    years = re.findall(r"\d{4}", period)
    if not years:
        raise ValueError(f"No year in title period {period!r} in {pdf_path.name}")
    return parse_week_start(period, int(years[-1]))


if __name__ == "__main__":
    pdf_path = sorted(Path("data/raw/ncr").glob("*.pdf"))[-1]
    rows = parse_report(pdf_path)

    print("File:", pdf_path.name)
    print("Price rows:", len(rows))

    print("\nRows per city:")
    for city, count in Counter(row["city"] for row in rows).most_common():
        print(f"  {city:<18} {count}")

    print("\nFirst 5 rows:")
    for row in rows[:5]:
        print(" ", row)