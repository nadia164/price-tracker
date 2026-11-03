from pathlib import Path

import pdfplumber

SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "text"}

pdf_path = sorted(Path("data/raw/ncr").glob("*.pdf"))[-1]
print("File:", pdf_path.name)

with pdfplumber.open(pdf_path) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):
        print(f"\n===== PAGE {page_number} =====")

        # Assumption A: what does the product column look like, row by row?
        table = page.extract_table(SETTINGS)
        print("--- Product column ---")
        for index, row in enumerate(table):
            print(f"{index:>3}  {row[0]!r}")

        # Assumption B: what text is in the AREA column?
        area_column = page.crop((0, 0, 86, page.height))
        print("--- AREA column text ---")
        print(area_column.extract_text())