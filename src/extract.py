import requests

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

if __name__ == "__main__":
    result = fetch_page(NCR_URL)
    print(len(result))
    print("October 20" in result)
