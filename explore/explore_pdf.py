from pathlib import Path

import pdfplumber

pdf_files = sorted(Path("data/raw/ncr").glob("*.pdf"))
pdf_path = pdf_files[-1]          # the newest, since names are dates
print("File:", pdf_path.name)

with pdfplumber.open(pdf_path) as pdf:
    print("Pages:", len(pdf.pages))

    first_page = pdf.pages[0]

    print("\n--- TEXT (first 1500 characters) ---")
    print(first_page.extract_text()[:1500])

    tables = first_page.extract_tables()
    print("\n--- TABLES on page 1:", len(tables), "---")
    if tables:
        for row in tables[0][:10]:
            print(row)