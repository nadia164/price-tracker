from collections import Counter
from pathlib import Path

import pdfplumber

TABLE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "text"}
AREA_COLUMN_RIGHT_EDGE = 86
FIRST_PRODUCT = "RON 100"
FOOTER_START = "Date of Monitoring"
EXPECTED_BRANDS = [
    "PETRON", "SHELL", "CALTEX", "PHOENIX", "TOTAL",
    "FLYING V", "UNIOIL", "SEAOIL", "PTT", "INDEPENDENT",
]


def get_column_positions(table):
    """Combine the two header rows and return {column name: column index}."""
    positions = {}
    for index, (top, bottom) in enumerate(zip(table[0], table[1])):
        name = (top or bottom or "").strip()
        if name:
            positions[name] = index

    required = ["PRODUCT"] + EXPECTED_BRANDS
    missing = [name for name in required if name not in positions]
    if missing:
        raise ValueError(f"Missing columns {missing}; found {list(positions)}")
    return positions


def read_city_names(page):
    """Return the city names in the AREA column, top to bottom."""
    area_column = page.crop((0, 0, AREA_COLUMN_RIGHT_EDGE, page.height))
    words = area_column.extract_words(use_text_flow=True)

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
        names.append(line["text"])
    return names


def parse_price_range(cell):
    """Turn '82.40 88.50' into (82.4, 88.5). Return None for an empty cell."""
    text = (cell or "").strip()
    if not text:
        return None

    parts = text.split()
    if len(parts) != 2:
        raise ValueError(f"Unexpected price cell: {cell!r}")

    low, high = float(parts[0]), float(parts[1])
    if low > high:
        raise ValueError(f"Low price is above high price: {cell!r}")
    return low, high


def parse_page(page, seen_cities):
    """Return (price rows, city names) for one page of a report."""
    table = page.extract_table(TABLE_SETTINGS)
    if not table:
        raise ValueError(f"No table found on page {page.page_number}")

    columns = get_column_positions(table)
    product_column = columns["PRODUCT"]
    cities = [name for name in read_city_names(page) if name not in seen_cities]

    rows = []
    city_index = -1
    for row in table:
        product = (row[product_column] or "").strip()
        if product in ("", "PRODUCT"):
            continue
        if product == FIRST_PRODUCT:
            city_index += 1
        if city_index < 0 or city_index >= len(cities):
            raise ValueError(
                f"Page {page.page_number}: can't match {product!r} to a city "
                f"(block {city_index + 1}, cities {cities})"
            )

        for brand in EXPECTED_BRANDS:
            price = parse_price_range(row[columns[brand]])
            if price is None:
                continue
            rows.append({
                "city": cities[city_index],
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
    return rows, cities


def parse_report(pdf_path):
    """Return every price row in one weekly report PDF."""
    all_rows = []
    seen_cities = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            rows, cities = parse_page(page, seen_cities)
            all_rows.extend(rows)
            seen_cities.update(cities)
    return all_rows


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