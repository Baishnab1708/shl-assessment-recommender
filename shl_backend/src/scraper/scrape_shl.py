import requests
import time
import csv
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"
PAGE_SIZE = 12
CATALOG_TYPES = [1, 2]
OUTPUT_FILE = "shl_products_details.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

TEST_TYPE_MAPPING = {
    'A': 'Ability & Aptitude',
    'B': 'Biodata & Situational Judgement',
    'C': 'Competencies',
    'D': 'Development & 360',
    'E': 'Assessment Exercises',
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'S': 'Simulations'
}


session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ---------------- HELPERS ---------------- #

def fetch(url, params=None):
    try:
        r = session.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=(10, 40)
        )
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Fetch failed: {url} params={params} → {e}")
        return None


def extract_test_types(td):
    codes = []
    for span in td.select("span"):
        c = span.get_text(strip=True)
        if c in TEST_TYPE_MAPPING:
            codes.append(TEST_TYPE_MAPPING[c])
    return ", ".join(codes)


def extract_product_details(url):
    html = fetch(url)
    if not html:
        return ("", "")

    soup = BeautifulSoup(html, "html.parser")

    def get_text(label):
        h = soup.find("h4", string=lambda x: x and label in x)
        if h:
            p = h.find_next_sibling("p")
            if p:
                return p.get_text(strip=True)
        return ""

    description = get_text("Description")
    duration = get_text("Assessment length")

    return (description, duration)



def main():
    seen_urls = set()
    products = []

    print(" Starting SHL full catalog scrape...")

    for catalog_type in CATALOG_TYPES:
        print(f"\n🔹 Catalog type = {catalog_type}")
        start = 0

        while True:
            print(f"  → Page start={start}")
            html = fetch(CATALOG_URL, params={"start": start, "type": catalog_type})
            if not html:
                start += PAGE_SIZE
                time.sleep(3)
                continue

            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select("table tbody tr")
            if not rows:
                break

            new_rows = 0

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue

                link = cols[0].find("a")
                if not link:
                    continue

                href = link.get("href", "").strip()
                if not href.startswith("/products/product-catalog/view/"):
                    continue

                url = BASE_URL + href
                if url in seen_urls:
                    continue

                name = link.get_text(strip=True)
                remote = "Yes" if cols[1].select_one(".green") else "No"
                adaptive = "Yes" if cols[2].select_one(".green") else "No"
                test_type = extract_test_types(cols[3])

                description, duration = extract_product_details(url)

                products.append([
                    name,
                    description,
                    url,
                    remote,
                    adaptive,
                    duration,
                    test_type
                ])

                seen_urls.add(url)
                new_rows += 1
                time.sleep(1.2)

            if new_rows == 0:
                break

            start += PAGE_SIZE
            time.sleep(2)

    print(f"\nTotal products collected: {len(products)}")

    if len(products) < 377:
        raise RuntimeError("Less than 377 Individual Test Solutions collected")

    # ---------------- SAVE CSV ---------------- #

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name",
            "Description",
            "URL",
            "Remote Testing",
            "Adaptive/IRT Support",
            "Duration",
            "Test Type"
        ])
        writer.writerows(products)

    print(f"Saved file → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
