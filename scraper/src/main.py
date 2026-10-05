from pathlib import Path
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl, ValidationError


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Satya-712/flyrank-w2-crud-api)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


class Book(BaseModel):
    title: str = Field(min_length=1)
    product_url: HttpUrl
    price_text: str = Field(min_length=1)
    price_gbp: float = Field(ge=0)
    availability_text: str = Field(min_length=1)
    rating_text: str = Field(min_length=1)
    description: str | None = None
    source_page: HttpUrl
    fetched_at: str


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

            next_cache = (
                CACHE_DIR /
                f"catalogue-page-{catalogue_pages + 1}.html"
            )

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
        description_text = description.get_text(
            " ",
            strip=True
        )

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


def normalize_price(price_text):
    cleaned = price_text.replace("£", "").replace("Â", "").strip()
    return float(cleaned)


def normalize_and_validate(records):
    valid_records = []
    errors = []
    seen_urls = set()

    for index, record in enumerate(records, start=1):
        try:
            product_url = str(record["product_url"])

            if product_url in seen_urls:
                raise ValueError("Duplicate product_url")

            seen_urls.add(product_url)

            normalized = {
                **record,
                "product_url": product_url,
                "price_gbp": normalize_price(record["price_text"]),
            }

            book = Book.model_validate(normalized)

            valid_records.append(book.model_dump(mode="json"))

        except (ValidationError, ValueError, TypeError) as exc:
            errors.append({
                "record_index": index,
                "product_url": record.get("product_url"),
                "reason": str(exc),
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    books_file = OUTPUT_DIR / "books.json"
    errors_file = OUTPUT_DIR / "errors.json"

    books_file.write_text(
        json.dumps(
            valid_records,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    errors_file.write_text(
        json.dumps(
            errors,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"books_json={books_file}")
    print(f"errors_json={errors_file}")

    return valid_records, errors


def extract_all_books():
    book_urls = discover_books()
    records = []

    for index, product_url in enumerate(book_urls, start=1):
        source_page = (
            f"{BASE_URL}catalogue/page-"
            f"{((index - 1) // 20) + 1}.html"
        )

        print(f"DETAIL {index}/{len(book_urls)}: {product_url}")

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
    raw_records = extract_all_books()
    normalize_and_validate(raw_records)