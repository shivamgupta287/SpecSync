import re
import logging
from urllib.parse import urljoin
from .fetcher import fetch, BASE_URL

log = logging.getLogger("scraper.specs")


# ------------------------------------------------------------------ #
# Quick search helpers
# ------------------------------------------------------------------ #

def _is_phone_url(href: str) -> bool:
    """
    GSMArena phone pages look like:  samsung_galaxy_s24-12024.php
    Brand listing pages look like:   samsung-phones-9.php
    We accept only URLs ending with  -<digits>.php  and containing an underscore
    (which brand listing URLs never have).
    """
    return bool(re.search(r"_.*-\d+\.php$", href))


def _extract_first_result(soup) -> dict | None:
    """
    GSMArena uses different containers on different pages.
    Try every known selector, filtering strictly for phone-page URLs.
    """
    selectors = [
        ("div", {"id": "review-body"}),
        ("div", {"class": "makers"}),
        ("div", {"class": "section-body"}),
    ]
    for tag, attrs in selectors:
        container = soup.find(tag, attrs)
        if not container:
            continue
        for li in container.find_all("li"):
            a = li.find("a", href=True)
            if not a or not _is_phone_url(a["href"]):
                continue
            span = a.find("span")
            name = span.get_text(strip=True) if span else a.get_text(strip=True)
            if name:
                return {"name": name, "url": urljoin(BASE_URL, a["href"])}

    return None


def _next_page_url(soup) -> str | None:
    """
    GSMArena puts pagination inside a container (div/p) with class 'nav-pages',
    not on the <a> tags themselves. Find the container first, then look inside it.
    """
    # Primary: find ANY tag with class nav-pages (div, p, span — doesn't matter)
    nav = soup.find(class_="nav-pages")
    if nav:
        log.debug(f"nav-pages container found ({nav.name}), links: {[a.get_text(strip=True) for a in nav.find_all('a')]}")
        for a in nav.find_all("a", href=True):
            text = a.get_text(strip=True)
            title = a.get("title", "").lower()
            if text in (">", "›", "»", "Next") or "next" in title:
                return urljoin(BASE_URL, a["href"])
    else:
        log.debug("No nav-pages container found on this page.")

    # Fallback: any <a title="Next page"> anywhere on the page
    for a in soup.find_all("a", title=True, href=True):
        if "next" in a["title"].lower():
            return urljoin(BASE_URL, a["href"])

    return None


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #

def search_phone(query: str) -> dict | None:
    log.info(f"Searching for phone: '{query}'")

    # Attempt 1: GSMArena quick search
    log.debug("Trying quick search endpoint ...")
    soup = fetch(f"{BASE_URL}/search.php3?sQuickSearch={query.replace(' ', '+')}")
    if soup:
        result = _extract_first_result(soup)
        if result:
            log.info(f"Quick search matched: {result['name']}")
            return result
        log.warning("Quick search: page loaded but no phone links found in any known container.")
    else:
        log.warning("Quick search fetch failed entirely.")

    # Attempt 2: Brand listing fuzzy match
    log.info("Falling back to brand-listing search ...")
    return _search_via_brand_listing(query)


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity: intersection / union. Penalises phones with extra tokens."""
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _pick_from_list(candidates: list[dict]) -> dict | None:
    """Print a numbered list and let the user choose interactively."""
    print("\nMultiple phones found. Please select one:\n")
    for i, c in enumerate(candidates, 1):
        print(f"  {i:>2}. {c['name']}")
    print(f"   0. Cancel\n")
    while True:
        try:
            choice = int(input("Enter number: ").strip())
            if choice == 0:
                return None
            if 1 <= choice <= len(candidates):
                return candidates[choice - 1]
            print(f"Please enter a number between 0 and {len(candidates)}.")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return None


def _search_via_brand_listing(query: str) -> dict | None:
    from .brands import get_all_brands

    query_lower = query.lower()
    query_tokens = set(query_lower.split())

    brands = get_all_brands()
    log.info(f"Loaded {len(brands)} brands.")

    # Longest-match first so "OnePlus" beats "One"
    matched_brand = None
    for brand in sorted(brands, key=lambda b: len(b["name"]), reverse=True):
        if brand["name"].lower() in query_lower:
            matched_brand = brand
            break

    if not matched_brand:
        log.error(
            f"No known brand found in query '{query}'. "
            f"Tip: include the brand name e.g. 'vivo iQOO Neo 10R', 'Samsung Galaxy S24'. "
            f"Known brands sample: {[b['name'] for b in brands[:15]]}"
        )
        return None

    log.info(f"Brand detected: {matched_brand['name']} — scanning listing pages ...")

    # Strip brand tokens so "vivo iQOO Neo 10R" searches with {"iqoo","neo","10r"}
    # and "iQOO Neo 10R" (listed without brand prefix) still scores correctly.
    brand_tokens = set(matched_brand["name"].lower().split())
    search_tokens = query_tokens - brand_tokens or query_tokens
    log.debug(f"Search tokens after stripping brand: {search_tokens}")

    page_url = matched_brand["url"]
    candidates: list[dict] = []
    page_num = 1

    while page_url:
        log.debug(f"Scanning brand page {page_num}: {page_url}")
        soup = fetch(page_url)
        if not soup:
            log.error(f"Failed to fetch brand page {page_num}.")
            break

        listing = soup.find("div", id="review-body")
        if not listing:
            log.error(f"Brand page {page_num}: #review-body not found.")
            log.debug(f"Page snippet: {soup.get_text()[:300]}")
            break

        for li in listing.find_all("li"):
            a = li.find("a")
            if not a:
                continue
            span = a.find("span")
            name = span.get_text(strip=True) if span else a.get_text(strip=True)
            name_tokens = set(name.lower().split())

            # Jaccard: penalises phones with extra tokens (e.g. "FE", "Ultra", "+")
            # so "Galaxy S24" scores higher than "Galaxy S24 FE" when query is "Galaxy S24"
            score = _jaccard(search_tokens, name_tokens)
            log.debug(f"  score={score:.2f}  {name}")

            if score >= 0.5:
                candidates.append({"name": name, "url": urljoin(BASE_URL, a.get("href", "")), "score": score})

        next_url = _next_page_url(soup)
        log.debug(f"{'Next page: ' + next_url if next_url else 'No more pages after page ' + str(page_num)}")
        page_url = next_url
        page_num += 1

    if not candidates:
        log.error("No match found across all brand listing pages.")
        return None

    candidates.sort(key=lambda c: c["score"], reverse=True)
    top = candidates[0]

    # Clear winner: top score is significantly ahead of second place
    if len(candidates) == 1 or candidates[0]["score"] - candidates[1]["score"] >= 0.2:
        log.info(f"Auto-selected (score={top['score']:.2f}): {top['name']}")
        return top

    # Ambiguous — let user pick
    log.info(f"{len(candidates)} candidates found — asking user to choose.")
    return _pick_from_list(candidates)


def search_phone_candidates(query: str) -> list[dict]:
    """
    Non-interactive version of search_phone for API use.
    Returns all scored candidates (score >= 0.5) sorted by score descending,
    without ever prompting the user.
    """
    log.info(f"Searching candidates for: '{query}'")

    soup = fetch(f"{BASE_URL}/search.php3?sQuickSearch={query.replace(' ', '+')}")
    if soup:
        result = _extract_first_result(soup)
        if result:
            log.info(f"Quick search matched: {result['name']}")
            result["score"] = 1.0
            return [result]

    from .brands import get_all_brands
    query_lower = query.lower()
    query_tokens = set(query_lower.split())
    brands = get_all_brands()

    matched_brand = None
    for brand in sorted(brands, key=lambda b: len(b["name"]), reverse=True):
        if brand["name"].lower() in query_lower:
            matched_brand = brand
            break

    if not matched_brand:
        log.warning(f"No brand found in query '{query}' — returning empty candidates.")
        return []

    brand_tokens = set(matched_brand["name"].lower().split())
    search_tokens = query_tokens - brand_tokens or query_tokens
    candidates: list[dict] = []
    page_url = matched_brand["url"]
    page_num = 1

    while page_url:
        soup = fetch(page_url)
        if not soup:
            break
        listing = soup.find("div", id="review-body")
        if not listing:
            break
        for li in listing.find_all("li"):
            a = li.find("a")
            if not a:
                continue
            span = a.find("span")
            name = span.get_text(strip=True) if span else a.get_text(strip=True)
            score = _jaccard(search_tokens, set(name.lower().split()))
            if score >= 0.5:
                candidates.append({"name": name, "url": urljoin(BASE_URL, a.get("href", "")), "score": score})
        page_url = _next_page_url(soup)
        page_num += 1

    candidates.sort(key=lambda c: c["score"], reverse=True)
    log.info(f"Found {len(candidates)} candidates for '{query}'")
    return candidates


def get_phone_specs(phone_url: str) -> dict | None:
    log.info(f"Fetching specs from: {phone_url}")
    soup = fetch(phone_url)
    if not soup:
        log.error("Failed to fetch phone spec page.")
        return None

    result: dict = {"url": phone_url, "specs": {}}

    h1 = soup.find("h1", class_="specs-phone-name-title")
    if h1:
        result["name"] = h1.get_text(strip=True)
        log.info(f"Phone name: {result['name']}")
    else:
        log.warning("Could not find phone name (<h1 class='specs-phone-name-title'> missing).")

    img_div = soup.find("div", class_="specs-photo-main")
    if img_div and img_div.find("img"):
        result["image_url"] = img_div.find("img").get("src")

    for table in soup.find_all("table"):
        category = None
        for row in table.find_all("tr"):
            th = row.find("th")
            if th:
                category = th.get_text(strip=True)
                continue
            tds = row.find_all("td")
            if len(tds) < 2:
                continue
            key = tds[0].get_text(strip=True)
            value = tds[1].get_text(separator=" ", strip=True)
            label = f"{category} > {key}" if category else key
            result["specs"][label] = value

    log.info(f"Extracted {len(result['specs'])} spec fields.")
    return result
