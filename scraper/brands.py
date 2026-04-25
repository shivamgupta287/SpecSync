import re
import logging
import bs4
from urllib.parse import urljoin
from .fetcher import fetch, BASE_URL

log = logging.getLogger("scraper.brands")


def get_all_brands() -> list[dict]:
    log.info("Fetching brand list from makers.php3 ...")
    soup = fetch(f"{BASE_URL}/makers.php3")
    if not soup:
        log.error("Failed to fetch makers page — got no response.")
        return []

    table = soup.find("table")
    if not table:
        log.error("Makers page loaded but <table> not found — page structure may have changed or a bot-check page was returned.")
        log.debug(f"Page snippet: {soup.get_text()[:300]}")
        return []

    brands = []
    for td in table.find_all("td"):
        a = td.find("a")
        if not a:
            continue

        # The <a> tag contains both the brand name (text node) and a <span> with
        # the device count. get_text() would merge them into "Apple147 devices",
        # so we read only the direct text node of <a>, ignoring child tags.
        name = "".join(
            s for s in a.children if isinstance(s, bs4.NavigableString)
        ).strip()

        count = 0
        span = a.find("span")
        if span:
            m = re.search(r"(\d+)", span.get_text())
            if m:
                count = int(m.group(1))

        if not name:
            continue

        brands.append({
            "name": name,
            "url": urljoin(BASE_URL, a.get("href", "")),
            "phone_count": count,
        })

    log.info(f"Found {len(brands)} brands.")
    return brands


def find_brand(name: str) -> dict | None:
    log.info(f"Looking up brand: '{name}'")
    brands = get_all_brands()
    for b in brands:
        if name.lower() in b["name"].lower():
            log.info(f"Matched brand: {b['name']} ({b['phone_count']} phones)")
            return b
    log.warning(f"No brand matched '{name}'.")
    return None
