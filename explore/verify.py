import sqlite3

conn = sqlite3.connect("data/prices.db")


def show(title, sql):
    print(f"\n=== {title} ===")
    for row in conn.execute(sql):
        print("  ", row)


show("Overall totals", """
    SELECT COUNT(DISTINCT week_start) AS weeks, MIN(week_start), MAX(week_start),
           COUNT(*) AS price_rows
    FROM prices
""")

show("1. Split city kept its rows (Parañaque, Mar-Apr 2026)", """
    SELECT week_start, COUNT(*) FROM prices
    WHERE city = 'Parañaque City' AND week_start BETWEEN '2026-03-03' AND '2026-04-14'
    GROUP BY week_start ORDER BY week_start
""")

show("2. PETRON RON 91 on 2025-04-15, all cities (compare with PDF page 1)", """
    SELECT city, price_low, price_high FROM prices
    WHERE week_start = '2025-04-15' AND product = 'RON 91' AND brand = 'PETRON'
    ORDER BY city
""")

show("3. City list", """
    SELECT city, COUNT(*) FROM prices GROUP BY city ORDER BY city
""")

show("4. Outlier week 2026-05-19 vs 2026-05-12, rows per city", """
    SELECT city,
           SUM(week_start = '2026-05-12') AS may_12,
           SUM(week_start = '2026-05-19') AS may_19
    FROM prices
    WHERE week_start IN ('2026-05-12', '2026-05-19')
    GROUP BY city ORDER BY city
""")

show("5. Zero prices (expect 0)", """
    SELECT COUNT(*) FROM prices WHERE price_low = 0 OR price_high = 0
""")

show("6. May 12 vs May 19, rows per brand", """
    SELECT brand,
           SUM(week_start = '2026-05-12') AS may_12,
           SUM(week_start = '2026-05-19') AS may_19
    FROM prices
    WHERE week_start IN ('2026-05-12', '2026-05-19')
    GROUP BY brand ORDER BY brand
""")

show("7. First and last week per city", """
    SELECT city, MIN(week_start), MAX(week_start), COUNT(DISTINCT week_start) AS weeks
    FROM prices GROUP BY city ORDER BY MIN(week_start), city
""")

show("8. Gaps between consecutive weeks (expect none over 7 days)", """
    SELECT prev_week, week_start,
           julianday(week_start) - julianday(prev_week) AS days_apart
    FROM (
        SELECT week_start,
               LAG(week_start) OVER (ORDER BY week_start) AS prev_week
        FROM (SELECT DISTINCT week_start FROM prices)
    )
    WHERE days_apart > 7
""")

conn.close()