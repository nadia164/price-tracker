import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from collections import Counter

NCR_URL = "https://doe.gov.ph/data-and-prices/liquid-fuels/retail-pump-prices/ncr-pump-prices"

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

    table = soup.find("table")

    if table is None:
        raise ValueError("No price table found on DOE NCR page.")

    links = table.find_all("a")
    
    reports = []
    for link in links:
        text = link.get_text(strip=True)
        url = link.get("href")

        reports.append({
            "text": text,
            "url": url
        })
    return reports


if __name__ == "__main__":
    result = fetch_page(NCR_URL)
    links = find_report_links(result)
    print("Total links:", len(links))

    domains = []
    for link in links:
        if link["url"] is None:
            continue

        parsed_url = urlparse(link["url"])
        domains.append(parsed_url.netloc)

    domains_count = Counter(domains)

    print("\nMost common domains:")
    print(domains_count.most_common())
