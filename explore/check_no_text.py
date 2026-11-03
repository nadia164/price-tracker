from pathlib import Path

import pdfplumber

for pdf_path in sorted(Path("data/raw/ncr").glob("*.pdf")):
    with pdfplumber.open(pdf_path) as pdf:
        chars = sum(len(page.chars) for page in pdf.pages)
        images = sum(len(page.images) for page in pdf.pages)
        if chars == 0:
            print(f"{pdf_path.name}: {len(pdf.pages)} pages, {chars} characters, {images} images")