import re
from collections import Counter
from pathlib import Path

lines = Path("logs/pipeline.log").read_text(encoding="utf-8").splitlines()

# Only look at the most recent run
last_start = max(i for i, line in enumerate(lines) if "Pipeline started" in line)
lines = lines[last_start:]

reasons = Counter()
examples = {}
for line in lines:
    if "Skipped " in line:
        message = line.split("Skipped ", 1)[1]
        kind = "SKIPPED"
    elif "Download failed" in line:
        message = line.split("Download failed for ", 1)[1]
        kind = "DOWNLOAD FAILED"
    else:
        continue

    file_name, _, reason = message.partition(": ")
    pattern = kind + "  " + re.sub(r"\d", "#", reason.split(";")[0])
    reasons[pattern] += 1
    examples.setdefault(pattern, []).append(file_name.split(" ")[0])

for pattern, count in reasons.most_common():
    print(f"{count:>4}  {pattern}")
    sample = examples[pattern]
    print(f"      first: {sample[0]}   last: {sample[-1]}")