# A9 — The Polite Scraper

## Target Classification

Target: Books to Scrape  
URL: https://books.toscrape.com/

Books to Scrape is a web scraping sandbox intended for learning and testing scraping technologies. It is a fictional bookstore and does not require login or JavaScript for the catalogue data.

## Robots.txt Check

Requested:

https://books.toscrape.com/robots.txt

Result: HTTP 404 Not Found.

The requested robots.txt file was not available at this URL.

## Scope

This scraper will process only the first 3 catalogue pages of Books to Scrape.

The expected scope is:
- 3 catalogue pages
- 60 unique book URLs
- Individual book detail pages
- No hardcoded book URLs

## Data Collected

For each book, the scraper will collect:

- title
- product_url
- price_text
- availability_text
- rating_text
- description
- source_page
- fetched_at

The normalized output will additionally contain:

- price_gbp

## Why This Target Is Appropriate

Books to Scrape is specifically provided as a safe web scraping practice sandbox. The project is limited to the first three catalogue pages and will use polite scraping practices such as an identifying User-Agent, request timeout, caching, and a delay between real requests.

I will not reuse this code on another site without checking its rules and terms first.

## Ethics

This project is for educational purposes.

When scraping real websites:
- Prefer an official API when one is available.
- Do not bypass logins, paywalls, access controls, or blocks.
- Collect only the data that is actually needed.
- Follow the site's rules and terms before reusing this scraper.
