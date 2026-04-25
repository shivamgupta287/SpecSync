import time
import logging
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.gsmarena.com"
log = logging.getLogger("scraper.fetcher")

_session = requests.Session()
_session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
})
_primed = False


def _prime_session():
    global _primed
    if _primed:
        return
    log.debug("Priming session — visiting homepage to collect cookies ...")
    try:
        resp = _session.get(BASE_URL, timeout=15)
        log.debug(f"Homepage status: {resp.status_code} | cookies: {dict(_session.cookies)}")
        time.sleep(1)
    except requests.RequestException as e:
        log.warning(f"Could not prime session: {e}")
    _primed = True


def fetch(url: str) -> BeautifulSoup | None:
    _prime_session()
    log.debug(f"GET {url}")
    try:
        resp = _session.get(url, timeout=15)
        log.debug(f"  → {resp.status_code} | {len(resp.text)} chars")
        resp.raise_for_status()
        time.sleep(1)
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        log.error(f"Request failed [{url}]: {e}")
        return None
