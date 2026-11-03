from pathlib import Path

import pdfplumber

SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "text"}

pdf_path = sorted(Path("data/raw/ncr").glob("*.pdf"))[-1]
print("File:", pdf_path.name)

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[1]                      # page 2 (counting starts at 0)
    table = page.extract_table(SETTINGS)

    print("--- Page 2: header rows in full ---")
    for row in table[:3]:
        print(row)

    print("\n--- Page 2: AREA and PRODUCT columns ---")
    for index, row in enumerate(table):
        print(f"{index:>3}  {row[0]!r:<32} {row[1]!r}")

    print("\n--- Page 2: last 3 rows in full ---")
    for row in table[-3:]:
        print(row)

    area_column = page.crop((0, 0, 86, page.height))

    print("\n--- AREA text: by position (default) ---")
    print(area_column.extract_text())

    print("\n--- AREA text: by drawing order ---")
    print(area_column.extract_text(use_text_flow=True))