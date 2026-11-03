# Data Notes

Known characteristics of the DOE NCR retail pump price reports, and how the
pipeline handles each one.

## Source quirks handled by the parser

| Quirk | Example | Handling |
|---|---|---|
| "NO LFRO" in a price cell | brand has no station in that city | Treated as no price |
| `0.00 0.00` | blank price written as zeros | Treated as no price |
| One price is zero, e.g. `78.00 0.00` | Valenzuela, DIESEL PLUS, Jun–Jul 2026 | Cell dropped and logged as a warning |
| City name typo | `Taguig Cty` | Corrected to `Taguig City` |
| Hidden duplicate city name on page 2 | overlapping "Caloocan City" text | Skipped: a city appears once per report |
| City block split across pages | 2026-03-10 to 2026-03-31 | Rows carried over to the open city |
| Extra "Prevailing Retail Prices" page | 2026-03-17, page 3 | Page skipped |
| Several links pointing to the same PDF | see download log | Each PDF downloaded once |

## Known gaps in the source

- **2026-05-19: no FLYING V prices.** The FLYING V column is blank in the
  DOE's PDF. Verified two ways: table extraction, and a word-position check
  using 2026-05-12 as a control (52 prices found there, 0 on 2026-05-19).
  Not filled in.

- **2025-05-27 and 2025-06-03: no reports.** The DOE page lists no reports
  between "May 20 to 26" and "June 10 to 16" in 2025. Detected by
  verify.py check 8 (a 21-day gap between consecutive weeks).

## Coverage changes

Not every city is monitored in every week, so NCR-wide averages can shift
because the set of cities changed, not because prices did.

| City | First week | Last week | Weeks |
|---|---|---|---|
| Caloocan, Makati, Manila, Muntinlupa, Parañaque, Pasay, Pasig, Quezon City, Taguig | 2025-03-04 | 2026-10-27 | 85 |
| Marikina, Navotas, Valenzuela | 2026-03-10 | 2026-10-27 | 34 |

## Not yet loaded

- Reports from 2017-01-03 to 2025-02-25 (399 files) use an older layout
  that the current parser does not support yet.