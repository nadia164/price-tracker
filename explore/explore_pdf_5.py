from pathlib import Path

import pdfplumber

pdf_path = sorted(Path("data/raw/ncr").glob("*.pdf"))[-1]
print("File:", pdf_path.name)

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[1]
    area_column = page.crop((0, 0, 86, page.height))

    words = area_column.extract_words(
        use_text_flow=True,
        extra_attrs=["non_stroking_color", "size"],
    )
    for word in words:
        print(f"{word['text']:<14} top={word['top']:7.1f}  "
              f"color={word['non_stroking_color']}  size={word['size']:.1f}")