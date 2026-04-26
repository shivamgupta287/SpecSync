import logging
from urllib.parse import urljoin
from .fetcher import fetch, BASE_URL

log = logging.getLogger("scraper.phones")


def get_phones_for_brand(brand_url: str, limit: int = 20) -> list[dict]:
    log.info(f"Fetching phones from: {brand_url} (limit={limit or 'all'})")
    phones = []
    page_url = brand_url
    page_num = 1

    while page_url:
        log.debug(f"Fetching page {page_num}: {page_url}")
        soup = fetch(page_url)
        if not soup:
            log.error(f"Failed to fetch page {page_num}.")
            break

        listing = soup.find("div", id="review-body")
        if not listing:
            log.error(f"Page {page_num} loaded but #review-body not found — possible bot-check page.")
            log.debug(f"Page snippet: {soup.get_text()[:300]}")
            break

        before = len(phones)
        for li in listing.find_all("li"):
            a = li.find("a")
            if not a:
                continue
            span = a.find("span")
            name = span.get_text(strip=True) if span else a.get_text(strip=True)
            phones.append({"name": name, "url": urljoin(BASE_URL, a.get("href", ""))})
            if limit and len(phones) >= limit:
                log.info(f"Limit reached ({limit}). Stopping.")
                return phones

        log.debug(f"Page {page_num}: +{len(phones) - before} phones (total so far: {len(phones)})")
        page_num += 1

        next_link = soup.find("a", class_="nav-pages", title="Next page")
        page_url = urljoin(BASE_URL, next_link["href"]) if next_link else None

    log.info(f"Total phones fetched: {len(phones)}")
    return phones
