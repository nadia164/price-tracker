from pathlib import Path

import pdfplumber

pdf_path = sorted(Path("data/raw/ncr").glob("*.pdf"))[-1]
print("File:", pdf_path.name)

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]

    # Experiment 1: SEE what the table finder detected
    image = page.to_image(resolution=150)
    image.debug_tablefinder()
    image.save("explore/table_debug.png")
    print("Saved explore/table_debug.png")

    # Experiment 2: use drawn lines for columns, text lines for rows
    settings = {"vertical_strategy": "lines", "horizontal_strategy": "text"}
    table = page.extract_table(settings)
    print("\n--- Experiment 2: first 12 rows ---")
    if table:
        for row in table[:12]:
            print(row)
    else:
        print("No table found with these settings")

    # Experiment 3: every word with its position on the page
    words = page.extract_words()
    print("\n--- Experiment 3: first 40 words ---")
    for word in words[:40]:
        print(f"{word['text']:<14} x0={word['x0']:7.1f}  top={word['top']:7.1f}")