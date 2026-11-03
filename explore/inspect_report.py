import sys
from pathlib import Path

import pdfplumber

from src.parse import TABLE_SETTINGS, read_city_names

RAW_DIR = Path("data/raw/ncr")

for file_name in sys.argv[1:]:
    pdf_path = RAW_DIR / file_name
    print("\n" + "#" * 70)
    print("FILE:", pdf_path.name)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            print(f"\n===== PAGE {page.page_number} of {len(pdf.pages)} =====")

            table = page.extract_table(TABLE_SETTINGS)
            if not table:
                print("No table found. Start of page text:")
                print((page.extract_text() or "")[:600])
                continue

            print("--- first 4 rows ---")
            for row in table[:4]:
                print(row)

            print("--- unusual cells ---")
            for row_number, row in enumerate(table):
                for cell in row:
                    parts = (cell or "").split()
                    if "0.00" in parts or "NO" in parts:
                        print(f"  row {row_number}: {cell!r}   full row: {row}")

            print("--- city names read from AREA column ---")
            print(" ", read_city_names(page))