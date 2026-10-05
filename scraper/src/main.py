from pathlib import Path
import time
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

            # Be polite between real requests.
            if not (CACHE_DIR / f"catalogue-page-{catalogue_pages + 1}.html").exists():
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


if __name__ == "__main__":
    discover_books()