import re
import sys

import pdfplumber

from src.parse import TABLE_SETTINGS

SINGLE_NUMBER = re.compile(r"^\d+\.\d+$")

for file_name in sys.argv[1:]:
    with pdfplumber.open(f"data/raw/ncr/{file_name}") as pdf:
        for page in pdf.pages:
            table = page.extract_table(TABLE_SETTINGS) or []
            for row_number, row in enumerate(table):
                for column, cell in enumerate(row):
                    if cell and SINGLE_NUMBER.match(cell.strip()):
                        print(f"{file_name} page {page.page_number} row {row_number} "
                              f"col {column}: {cell!r}")
                        print(f"    full row: {row}")