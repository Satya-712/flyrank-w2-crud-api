from pathlib import Path
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Satya-712/flyrank-w2-crud-api)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url, cache_file):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT: {cache_file}")
        print(f"response_size={len(html)} bytes")
        return html

    headers = {
        "User-Agent": USER_AGENT
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=TIMEOUT,
    )

    print(f"FETCH: {url}")
    print(f"status={response.status_code}")
    print(f"response_size={len(response.content)} bytes")

    if response.status_code != 200:
        raise RuntimeError(
            f"Unexpected HTTP status: {response.status_code}"
        )

    cache_file.write_text(response.text, encoding="utf-8")
    print(f"cached_to={cache_file}")

    return response.text


def discover_books():
    all_book_urls = []
    catalogue_pages = 0
    next_url = BASE_URL

    while next_url and catalogue_pages < 3:
        catalogue_pages += 1

        cache_file = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(next_url, cache_file)

        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_url = urljoin(next_url, link.get("href"))
            all_book_urls.append(book_url)

        next_link = soup.select_one("li.next a")

        if next_link:
            next_url = urljoin(next_url, next_link.get("href"))

            next_cache = CACHE_DIR / f"catalogue-page-{catalogue_pages + 1}.html"

            if not next_cache.exists():
                time.sleep(REQUEST_DELAY)
        else:
            next_url = None

    unique_urls = list(dict.fromkeys(all_book_urls))

    print(
        f"catalogue_pages={catalogue_pages} "
        f"discovered={len(all_book_urls)} "
        f"unique_urls={len(unique_urls)}"
    )

    return unique_urls


def extract_book_details(product_url, source_page, index):
    cache_file = CACHE_DIR / f"book-{index}.html"

    html = fetch_page(product_url, cache_file)

    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("div.product_main h1")
    price = soup.select_one("p.price_color")
    availability = soup.select_one("p.instock.availability")
    rating = soup.select_one("p.star-rating")
    description = soup.select_one("#product_description + p")

    rating_text = None
    if rating:
        classes = rating.get("class", [])
        rating_text = next(
            (item for item in classes if item != "star-rating"),
            None
        )

    description_text = None
    if description:
        description_text = description.get_text(" ", strip=True)

    return {
        "title": title.get_text(strip=True) if title else None,
        "product_url": product_url,
        "price_text": price.get_text(" ", strip=True) if price else None,
        "availability_text": (
            availability.get_text(" ", strip=True)
            if availability
            else None
        ),
        "rating_text": rating_text,
        "description": description_text,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def extract_all_books():
    book_urls = discover_books()
    records = []

    for index, product_url in enumerate(book_urls, start=1):
        source_page = (
            f"{BASE_URL}catalogue/page-"
            f"{((index - 1) // 20) + 1}.html"
        )

        print(f"DETAIL {index}/60: {product_url}")

        record = extract_book_details(
            product_url,
            source_page,
            index
        )

        records.append(record)

        if index < len(book_urls):
            cache_file = CACHE_DIR / f"book-{index + 1}.html"

            if not cache_file.exists():
                time.sleep(REQUEST_DELAY)

    print(f"detail_pages={len(records)}")

    if records:
        print("\nFIRST RAW RECORD:")
        print(records[0])

    return records


if __name__ == "__main__":
    extract_all_books()