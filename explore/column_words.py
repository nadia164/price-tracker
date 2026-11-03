import sys

import pdfplumber

file_name, left_word, right_word = sys.argv[1], sys.argv[2], sys.argv[3]

with pdfplumber.open(f"data/raw/ncr/{file_name}") as pdf:
    page = pdf.pages[0]
    words = page.extract_words()

    left = next(w for w in words if w["text"] == left_word)
    right = next(w for w in words if w["text"] == right_word)

    numbers = [
        w["text"] for w in words
        if left["x0"] - 15 < w["x0"] < right["x0"] - 10
        and w["top"] > left["bottom"]
        and w["text"][0].isdigit()
    ]
    print(f"{file_name}: {len(numbers)} numbers between {left_word} and {right_word}")
    print(numbers[:20])