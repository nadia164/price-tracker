import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from datetime import datetime
import time
from pathlib import Path


NCR_URL = "https://doe.gov.ph/data-and-prices/liquid-fuels/retail-pump-prices/ncr-pump-prices"
HEADERS = {"User-Agent": "PricetrackerLearning/0.1"}
WEEK_START_PATTERN = r"([A-Za-z]+)\s+(\d{1,2})(?:,\s*(\d{4}))?"
RAW_DIR = Path("data/raw/ncr")

def fetch_page(url):

    response = requests.get(url, headers=HEADERS, timeout=30)
    """ 
        response.status_code -> eg. 200
        response.text -> page content as a string
        response.raise_for_status() -> method that raises an error if the status code is bad
    """

    response.raise_for_status()

    return response.text

def find_report_links(html):
    """Return a list of report links found in the page HTML."""
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", class_="lex-table")

    if table is None:
        raise ValueError("No price table found on DOE NCR page.")

    # links = table.find_all("a")
    
    reports = []

    # for link in links:
    #     text = link.get_text(strip=True)
    #     url = link.get("href")

    #     reports.append({
    #         "text": text,
    #         "url": url
    #     })

    # for row in table:
    #     row.find(["td", "th"])

    #rows = table.find_all("tr")
    # print("Rows found:", len(rows))

    for row in table.find_all("tr"): 
        first_cell = row.find("td")
        if first_cell is None:
            continue
        year_text = first_cell.get_text(strip=True)
        if not year_text.isdigit() or len(year_text) != 4:
            continue
        # print("Year cell:", year_text)

        for link in row.find_all("a"):
            reports.append({
                "year": int(year_text),
                "text": link.get_text(strip=True),
                "url":  link.get("href")
            })
        # print(reports)

    return reports

def parse_week_start(text, row_year):
    """Return the start date of a report week from its link text."""
    match = re.search(WEEK_START_PATTERN, text)
    if match is None:
        raise ValueError(f"No start date found in link text: {text!r}")

    month = match.group(1)
    day = match.group(2)
    year = match.group(3) or row_year

    date_string = f"{month} {day} {year}"
    return datetime.strptime(date_string, "%B %d %Y").date()

def build_report_list(html):
    reports = []
    failures = []
    for report in find_report_links(html):
        try:
            report["week_start"] = parse_week_start(report["text"], report["year"])
            reports.append(report)
        except ValueError as error:
            report["error"] = str(error)
            failures.append(report)
    return reports, failures

def find_duplicate_urls(reports):
    url_counts = Counter(report["url"] for report in reports)

    duplicates = {}
    for report in reports:
        url = report["url"]
        if url_counts[url] > 1:
            if url not in duplicates:
                duplicates[url] = []
            duplicates[url].append(f"{report['text']} ({report['year']})")
    return duplicates

def download_pdf(url, file_path):
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise ValueError(f"Response is not a PDF: {url}")
    file_path.write_bytes(response.content)

def download_new_reports(reports, limit=None):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    newest_first = sorted(reports, key=lambda r: r["week_start"], reverse=True)
    if limit is not None:
        newest_first = newest_first[:limit]

    seen_urls = set()
    downloaded = 0
    skipped = 0

    for report in newest_first:
        if report["url"] in seen_urls:
            print(f" duplicate link, skipping: {report['text']} ({report['year']})")
            continue
        seen_urls.add(report["url"])

        file_path = RAW_DIR / f"{report['week_start']}.pdf"
        if file_path.exists():
            print(f" already have: {file_path.name}")
            skipped += 1
            continue

        download_pdf(report["url"], file_path)
        print(f" downloaded:  {file_path.name}")
        downloaded += 1
        time.sleep(1)

    print(f"\nDownloaded {downloaded}, skipped {skipped}")


if __name__ == "__main__":
    html = fetch_page(NCR_URL)

    # parse every link and check the totals
    reports, failures = build_report_list(html)
    print(f"Parsed: {len(reports)}   Failed: {len(failures)}   "
          f"Total: {len(reports) + len(failures)}")
    for failure in failures:
        print(f"  FAILED: {failure['year']} {failure['text']!r}")

    # report duplicate URLs
    duplicates = find_duplicate_urls(reports)
    print(f"\nURLs used by more than one week: {len(duplicates)}")
    for url, labels in duplicates.items():
        print("  " + "  |  ".join(labels))
        print(f"    {url}")

    # download only the newest 3 while testing
    print("\nDownloading newest reports...")
    download_new_reports(reports, limit=3)

    # result = fetch_page(NCR_URL)
    # links = find_report_links(result)
    # print("Total links:", len(links))

    # domains = []
    # for link in links:
    #     if link["url"] is None:
    #         continue

    #     parsed_url = urlparse(link["url"])
    #     domains.append(parsed_url.netloc)

    # domains_count = Counter(domains)

    # print("\nMost common domains:")
    # print(domains_count.most_common())
