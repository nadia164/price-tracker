import sys

import pdfplumber

from src.parse import TABLE_SETTINGS

for file_name in sys.argv[1:]:
    print("\n" + "#" * 70)
    print("FILE:", file_name)

    with pdfplumber.open(f"data/raw/ncr/{file_name}") as pdf:
        print("Pages:", len(pdf.pages))
        page = pdf.pages[0]

        print("\n--- page 1 text (first 800 characters) ---")
        print((page.extract_text() or "")[:800])

        print("\n--- page 1 table, our settings (first 10 rows) ---")
        table = page.extract_table(TABLE_SETTINGS)
        for row in (table or [])[:10]:
            print(row)