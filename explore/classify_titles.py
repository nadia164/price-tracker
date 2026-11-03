import re
from collections import defaultdict
from pathlib import Path

import pdfplumber

TITLE_STYLES = [
    ("current: 'For the week of'", r"For the week of"),
    ("2024-style: 'For the period of'", r"For the period of"),
    ("2021-style: 'Prevailing Retail Pump Price as of'", r"Prevailing Retail Pump Price\s+as of"),
    ("2017-style: 'Prevailing Retail Prices ... Metro Manila'",
     r"PREVAILING RETAIL PRICES OF PETROLEUM PRODUCTS IN METRO MANILA"),
]


def classify(text):
    for label, pattern in TITLE_STYLES:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return "UNKNOWN"

unknown_starts = {}
groups = defaultdict(list)
first_lines = {}
for pdf_path in sorted(Path("data/raw/ncr").glob("*.pdf")):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0].dedupe_chars()
        text = page.extract_text() or ""
    label = classify(text)
    groups[label].append(pdf_path.name)
    if label == "UNKNOWN":
        unknown_starts[pdf_path.name] = text.splitlines()[:2]
    first_lines.setdefault(label, text.splitlines()[:2])

for label, files in groups.items():
    years = sorted({name[:4] for name in files})
    print(f"\n{len(files):>4}  {label}")
    print(f"      first: {files[0]}   last: {files[-1]}   years: {', '.join(years)}")
    if label == "UNKNOWN":
        for name in files:
            print(f"      {name}: {unknown_starts[name]}")