from pathlib import Path
import requests

BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Satya-712/flyrank-w2-crud-api)"
TIMEOUT = 10


def fetch_catalogue_page():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        html = CACHE_FILE.read_text(encoding="utf-8")
        print(f"CACHE HIT: {CACHE_FILE}")
        print(f"response_size={len(html)} bytes")
        return html

    headers = {
        "User-Agent": USER_AGENT
    }

    response = requests.get(
        BASE_URL,
        headers=headers,
        timeout=TIMEOUT,
    )

    print(f"FETCH: {BASE_URL}")
    print(f"status={response.status_code}")
    print(f"response_size={len(response.content)} bytes")

    if response.status_code != 200:
        raise RuntimeError(
            f"Unexpected HTTP status: {response.status_code}"
        )

    CACHE_FILE.write_text(response.text, encoding="utf-8")
    print(f"cached_to={CACHE_FILE}")

    return response.text


if __name__ == "__main__":
    fetch_catalogue_page()