\# A9 — The Polite Scraper



\## Target Classification



Target: Books to Scrape

URL: https://books.toscrape.com/



Books to Scrape is a web scraping sandbox intended for learning and testing scraping technologies. It is a fictional bookstore and does not require login or JavaScript for the catalogue data.



\## Robots.txt Check



Requested:



https://books.toscrape.com/robots.txt



Result: HTTP 404 Not Found.



The requested robots.txt file was not available at this URL.



\## Scope



This scraper processes only the first 3 catalogue pages.



Expected scope:



\- 3 catalogue pages

\- 60 unique book URLs

\- Individual book detail pages

\- No hardcoded book URLs



The catalogue pages are followed dynamically using the site's `next` link.



\## Data Collected



For each book, the scraper collects:



\- `title`

\- `product\\\_url`

\- `price\\\_text`

\- `price\\\_gbp`

\- `availability\\\_text`

\- `rating\\\_text`

\- `description`

\- `source\\\_page`

\- `fetched\\\_at`



The raw extraction stage keeps the required provenance fields, while the validated output additionally contains the normalized numeric `price\\\_gbp`.



\## Pipeline



The scraper follows this pipeline:



```text

Fetch

\&#x20; ?

Extract

\&#x20; ?

Normalize

\&#x20; ?

Validate

\&#x20; ?

Store

\&#x20; ?

Report


