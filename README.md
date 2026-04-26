# GSMArena Scraper

A command-line tool to scrape phone specs and brand listings from GSMArena.

## About the Project

GSMArena is one of the most comprehensive databases of mobile phone specifications on the internet, covering thousands of devices across hundreds of brands. This project provides a lightweight Python CLI to extract that data programmatically — no browser required.

The scraper works by sending HTTP requests that mimic a real browser session (including cookies, headers, and a session warm-up visit to the homepage). It parses the returned HTML using BeautifulSoup and exposes the results through two simple commands: list all phones for a brand, or look up the full technical specifications of a specific phone.

Results are saved as structured JSON files so they can be consumed by other tools, scripts, or data pipelines. Every run also produces a detailed log file that records each HTTP request, parse decision, and search scoring step — useful for debugging or auditing what the scraper did.

The search logic uses a two-stage approach: it first tries GSMArena's own quick-search endpoint, and falls back to a fuzzy token-matching algorithm (Jaccard similarity) against the brand's full phone listing if the quick search returns nothing.

## Features

- Look up all phones for a given brand
- Search for a specific phone by name and fetch its full specs
- Saves results as timestamped JSON files in `output/`
- Writes detailed logs to `log/` on every run

## Requirements

- Python 3.10+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Search by brand

```bash
python main.py --brand Samsung
python main.py --brand OnePlus --limit 50
python main.py --brand Apple --limit 0   # 0 = fetch all pages
```

### Search by phone name

```bash
python main.py --phone "Apple iPhone 17 Pro"
python main.py --phone "Samsung Galaxy S24"
python main.py --phone "vivo iQOO Neo 10R"
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--brand BRAND` | Brand name to list phones for | — |
| `--phone PHONE` | Phone name to search and fetch specs | — |
| `--limit N` | Max phones to return for `--brand` (`0` = all) | `20` |

`--brand` and `--phone` are mutually exclusive.

## Output

**JSON files** are saved to `output/<name>_<timestamp>.json`.

- Brand query → `{ "brand": {...}, "phones": [...] }`
- Phone query → `{ "name": "...", "url": "...", "image_url": "...", "specs": {...} }`

**Log files** are written to `log/scraper_<timestamp>.log` on every run (one file per run). The `log/` directory is git-ignored.

## Project Structure

```
GSM/
├── main.py                  # CLI entry point
├── requirements.txt
├── output/                  # JSON results (git-ignored)
├── log/                     # Log files (git-ignored)
└── scraper/
    ├── __init__.py          # Package init — sets up logging
    ├── log_config.py        # Logging setup (file + console handlers)
    ├── fetcher.py           # HTTP session and page fetching
    ├── brands.py            # Brand listing and lookup
    ├── phones.py            # Phone listing for a brand
    ├── specs.py             # Phone search and spec extraction
    ├── display.py           # Console output formatting
    └── writer.py            # JSON file writer
```

## How search works

1. **Quick search** — hits `GSMArena/search.php3?sQuickSearch=<query>` first.
2. **Brand-listing fallback** — if quick search fails, detects the brand from the query, fetches that brand's listing pages, and ranks phones using Jaccard similarity on the remaining tokens. If the top match is ambiguous, the CLI prompts you to choose.
