import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from collections import Counter
import re
from datetime import datetime


NCR_URL = "https://doe.gov.ph/data-and-prices/liquid-fuels/retail-pump-prices/ncr-pump-prices"
WEEK_START_PATTERN = r"([A-Za-z]+)\s+(\d{1,2})(?:,\s*(\d{4}))?"

def fetch_page(url):
    headers = {"User-Agent": "PricetrackerLearning/0.1"}

    response = requests.get(url, headers=headers, timeout=30)
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


if __name__ == "__main__":
    tests = [
        ("October 20 to 26", 2026, "2026-10-20"),
        ("September 29 to October 5", 2026, "2026-09-29"),
        ("February 10-16", 2026, "2026-02-10"),
        ("April 29 to May 05", 2025, "2025-04-29"),
        ("January 4", 2024, "2024-01-04"),
        ("December 30, 2025 to January 5, 2026", 2025, "2025-12-30"),
        ("December 31, 2024 to January 6, 2025", 2025, "2024-12-31"),
    ]

    passed = 0
    for text, row_year, expected in tests:
        result = parse_week_start(text, row_year)
        status = "PASS" if str(result) == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"{status}  {text!r}  (row {row_year}) -> {result}  expected {expected}")

    print(f"\n{passed}/{len(tests)} tests passed")

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
