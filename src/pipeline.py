import argparse
import logging
import sys
from pathlib import Path

from src.extract import NCR_URL, RAW_DIR, build_report_list, download_new_reports, fetch_page
from src.load import REGION, connect, create_tables, load_all

LOG_DIR = Path("logs")
logger = logging.getLogger(__name__)


def setup_logging():
    """Send log messages to both the terminal and logs/pipeline.log."""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def run(limit):
    """Run extract, download, and load once. Return the number of problems found."""
    problems = 0

    logger.info("Fetching report list from DOE")
    html = fetch_page(NCR_URL)
    reports, failures = build_report_list(html)
    logger.info("Found %d report links (%d could not be dated)",
                len(reports) + len(failures), len(failures))
    for failure in failures:
        logger.warning("Could not date link %r (%s)", failure["text"], failure["year"])
    problems += len(failures)

    downloaded, already_had, failed = download_new_reports(reports, limit=limit)
    logger.info("Downloads: %d new, %d already had, %d failed",
                downloaded, already_had, failed)
    problems += failed

    conn = connect()
    try:
        create_tables(conn)
        loaded, skipped = load_all(conn, REGION, RAW_DIR)
    finally:
        conn.close()
    logger.info("Database: %d reports loaded, %d skipped", loaded, skipped)
    problems += skipped

    return problems


def main():
    parser = argparse.ArgumentParser(description="Download and load DOE NCR fuel price reports.")
    parser.add_argument(
        "--limit", type=int, default=5,
        help="download at most this many of the newest reports (default: 5)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="download every report on the page (ignores --limit)",
    )
    args = parser.parse_args()

    setup_logging()

    limit = None if args.all else args.limit
    logger.info("Pipeline started (limit=%s)", limit)

    try:
        problems = run(limit)
    except Exception:
        logger.exception("Pipeline crashed")
        return 2

    if problems:
        logger.warning("Pipeline finished with %d problem(s)", problems)
        return 1
    logger.info("Pipeline finished OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())