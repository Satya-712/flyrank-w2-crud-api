import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("output")

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Satya-712/flyrank-w2-crud-api)"
TIMEOUT = 10
DELAY = 0.5

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


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


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def fetch_page(url, cache_file, report):
    """
    Fetch a page with caching.

    - Cache hit: no real request.
    - Real request: timeout + status check.
    - Timeout/5xx: retry once after delay.
    - 403/404: no retry.
    """

    cache_path = CACHE_DIR / cache_file

    if cache_path.exists():
        content = cache_path.read_text(encoding="utf-8")
        report["cache_hits"] += 1
        print(f"CACHE HIT: {url}")
        print(f"response_size={len(content.encode('utf-8'))} bytes")
        return content

    attempts = 2

    for attempt in range(attempts):
        try:
            if report["pages_fetched"] > 0:
                time.sleep(DELAY)

            print(f"FETCH: {url}")

            response = session.get(url, timeout=TIMEOUT)
            report["pages_fetched"] += 1

            print(f"status={response.status_code}")

            if response.status_code == 200:
                content = response.text

                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(content, encoding="utf-8")

                print(f"response_size={len(response.content)} bytes")
                print(f"cached_to={cache_path}")

                return content

            # Retry only timeout/5xx-type failures.
            if response.status_code >= 500 and attempt == 0:
                print("5xx response - retrying once after delay")
                time.sleep(DELAY)
                continue

            # 403/404 and other non-200 responses are not retried.
            print(f"FAILED: HTTP {response.status_code}")
            return None

        except requests.Timeout:
            print("TIMEOUT")

            if attempt == 0:
                print("Retrying once after delay")
                time.sleep(DELAY)
                continue

            return None

        except requests.RequestException as exc:
            print(f"REQUEST ERROR: {exc}")
            return None

    return None


def parse_catalogue(html, source_url):
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for article in soup.select("article.product_pod"):
        link = article.select_one("h3 a")

        if link and link.get("href"):
            absolute_url = urljoin(source_url, link["href"])
            links.append(absolute_url)

    next_link = soup.select_one("li.next a")

    next_url = None

    if next_link and next_link.get("href"):
        next_url = urljoin(source_url, next_link["href"])

    return links, next_url


def normalize_price(price_text):
    cleaned = price_text.replace("£", "").replace("Â", "").strip()
    return float(cleaned)


def extract_book(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("div.product_main h1")
    price_tag = soup.select_one("p.price_color")
    availability_tag = soup.select_one("p.instock.availability")
    rating_tag = soup.select_one("div.product_main p.star-rating")

    title = title_tag.get_text(strip=True) if title_tag else ""

    price_text = price_tag.get_text(strip=True) if price_tag else ""

    availability_text = (
        availability_tag.get_text(" ", strip=True)
        if availability_tag
        else ""
    )

    rating_text = ""

    if rating_tag:
        classes = rating_tag.get("class", [])
        rating_words = {
            "One",
            "Two",
            "Three",
            "Four",
            "Five",
        }

        for item in classes:
            if item in rating_words:
                rating_text = item
                break

    description = None

    description_header = soup.find("div", id="product_description")

    if description_header:
        description_tag = description_header.find_next_sibling("p")

        if description_tag:
            description = description_tag.get_text(" ", strip=True)

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "price_gbp": normalize_price(price_text),
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": now_iso(),
    }


def main():
    start_time = time.time()

    CACHE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    report = {
        "start_time": now_iso(),
        "duration_seconds": 0,
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": [],
    }

    # ---------------------------------------------------------
    # Stage 2: Discover first 3 catalogue pages
    # ---------------------------------------------------------

    catalogue_urls = [BASE_URL]
    catalogue_pages = []

    current_url = BASE_URL

    for page_number in range(1, 4):
        cache_file = f"catalogue-page-{page_number}.html"

        html = fetch_page(
            current_url,
            cache_file,
            report,
        )

        if html is None:
            report["failed_pages"].append(current_url)
            break

        catalogue_pages.append(current_url)

        links, next_url = parse_catalogue(
            html,
            current_url,
        )

        if page_number < 3:
            current_url = next_url

            if current_url is None:
                break

    product_urls = []

    for page_url in catalogue_pages:
        page_number = catalogue_pages.index(page_url) + 1

        cache_file = f"catalogue-page-{page_number}.html"

        html = (CACHE_DIR / cache_file).read_text(
            encoding="utf-8"
        )

        links, _ = parse_catalogue(
            html,
            page_url,
        )

        product_urls.extend(links)

    unique_product_urls = list(dict.fromkeys(product_urls))

    print(
        f"catalogue_pages={len(catalogue_pages)} "
        f"discovered={len(product_urls)} "
        f"unique_urls={len(unique_product_urls)}"
    )

    # ---------------------------------------------------------
    # Stage 3 + Stage 5: Fetch detail pages
    # ---------------------------------------------------------

    raw_records = []

    for index, product_url in enumerate(unique_product_urls, start=1):

        # Deliberately inject one broken URL for Stage 5 testing.
        # This gives us one failed page without affecting the
        # original 60 discovered book URLs.
        if index == 1:
            test_url = "https://books.toscrape.com/catalogue/this-page-does-not-exist.html"

            html = fetch_page(
                test_url,
                "book-broken-test.html",
                report,
            )

            if html is None:
                report["failed_pages"].append(test_url)
                print(f"FAILED PAGE SKIPPED: {test_url}")

        cache_file = f"book-{index}.html"

        html = fetch_page(
            product_url,
            cache_file,
            report,
        )

        if html is None:
            report["failed_pages"].append(product_url)
            print(f"FAILED PAGE SKIPPED: {product_url}")
            continue

        source_page = (
            f"{BASE_URL}catalogue/page-"
            f"{((index - 1) // 20) + 1}.html"
        )

        try:
            record = extract_book(
                html,
                product_url,
                source_page,
            )

            raw_records.append(record)

            print(
                f"DETAIL {index}/{len(unique_product_urls)}: "
                f"{record['title']}"
            )

        except Exception as exc:
            report["failed_pages"].append(product_url)
            print(
                f"FAILED PAGE SKIPPED: "
                f"{product_url} reason={exc}"
            )

    print(f"detail_pages={len(raw_records)}")

    # ---------------------------------------------------------
    # Stage 4: Validate normalized records
    # ---------------------------------------------------------

    valid_records = []
    errors = []

    seen_urls = set()

    for record in raw_records:
        try:
            book = Book(**record)

            canonical_url = str(book.product_url)

            if canonical_url in seen_urls:
                raise ValueError(
                    f"Duplicate product_url: {canonical_url}"
                )

            seen_urls.add(canonical_url)

            valid_records.append(
                book.model_dump(mode="json")
            )

        except Exception as exc:
            errors.append(
                {
                    "record": record,
                    "reason": str(exc),
                }
            )

    books_path = OUTPUT_DIR / "books.json"
    errors_path = OUTPUT_DIR / "errors.json"
    report_path = OUTPUT_DIR / "run-report.json"

    books_path.write_text(
        json.dumps(
            valid_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    errors_path.write_text(
        json.dumps(
            errors,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    report["valid_records"] = len(valid_records)
    report["invalid_records"] = len(errors)
    report["duration_seconds"] = round(
        time.time() - start_time,
        3,
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("VALIDATION RESULT")
    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"books_json={books_path}")
    print(f"errors_json={errors_path}")
    print(f"run_report={report_path}")
    print(f"failed_pages={len(report['failed_pages'])}")


if __name__ == "__main__":
    main()