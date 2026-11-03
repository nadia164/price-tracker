import sqlite3
from datetime import date, datetime
from pathlib import Path
import logging

from src.parse import parse_report, read_title_week_start

DB_PATH = Path("data/prices.db")
SCHEMA_PATH = Path("sql/schema.sql")
RAW_DIR = Path("data/raw/ncr")
REGION = "NCR"

logger = logging.getLogger(__name__)


def connect():
    """Open the database and turn on foreign key checks."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    """Create the tables if they don't exist yet."""
    conn.executescript(SCHEMA_PATH.read_text())


def is_loaded(conn, region, week_start):
    """Return True if this region's week is already in the database."""
    cursor = conn.execute(
        "SELECT 1 FROM reports WHERE region = ? AND week_start = ?",
        (region, week_start.isoformat()),
    )
    return cursor.fetchone() is not None


def load_report(conn, region, pdf_path):
    """Load one PDF into the database. Return the number of price rows added."""
    week_start = date.fromisoformat(pdf_path.stem)
    if is_loaded(conn, region, week_start):
        return 0

    title_week_start = read_title_week_start(pdf_path)
    if title_week_start != week_start:
        raise ValueError(
            f"file name says {week_start} but PDF title says {title_week_start}"
        )

    rows = parse_report(pdf_path)
    price_values = [
        (region, week_start.isoformat(), row["city"], row["product"],
         row["brand"], row["price_low"], row["price_high"])
        for row in rows
    ]

    with conn:
        conn.execute(
            "INSERT INTO reports (region, week_start, file_name, loaded_at) "
            "VALUES (?, ?, ?, ?)",
            (region, week_start.isoformat(), pdf_path.name,
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.executemany(
            "INSERT INTO prices (region, week_start, city, product, brand, "
            "price_low, price_high) VALUES (?, ?, ?, ?, ?, ?, ?)",
            price_values,
        )
    return len(rows)


def load_all(conn, region, raw_dir):
    """Load every PDF in raw_dir that isn't in the database yet. Return (loaded, skipped)."""
    loaded = 0
    skipped = 0
    for pdf_path in sorted(raw_dir.glob("*.pdf")):
        try:
            count = load_report(conn, region, pdf_path)
        except Exception as error:
            logger.warning("Skipped %s: %s: %s", pdf_path.name, type(error).__name__, error)
            skipped += 1
            continue
        if count:
            logger.info("Loaded %s: %d price rows", pdf_path.name, count)
            loaded += 1
    return loaded, skipped


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = connect()
    create_tables(conn)
    load_all(conn, REGION, RAW_DIR)

    total = conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
    print(f"Price rows in database: {total}")

    query = """
        SELECT product,
               COUNT(*)                  AS brand_city_count,
               ROUND(AVG(price_low), 2)  AS avg_low,
               ROUND(AVG(price_high), 2) AS avg_high
        FROM prices
        WHERE week_start = (SELECT MAX(week_start) FROM prices)
        GROUP BY product
        ORDER BY avg_low
    """
    print("\nLatest week, average prices by product:")
    for product, count, avg_low, avg_high in conn.execute(query):
        print(f"  {product:<12} {count:>3} rows   low {avg_low:>7}   high {avg_high:>7}")

    conn.close()