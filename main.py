#!/usr/bin/env python3
"""
GSMArena Scraper — Entry Point
-------------------------------
Usage:
  python main.py --brand Samsung
  python main.py --brand OnePlus --limit 50
  python main.py --phone "Apple iPhone 17 Pro"
"""

import argparse
import logging
import sys

from scraper import (
    find_brand,
    get_phones_for_brand,
    search_phone,
    get_phone_specs,
    print_phone_list,
    print_specs,
    save_to_json,
)

log = logging.getLogger("main")


def cmd_brand(brand_name: str, limit: int):
    log.info(f"Looking up brand: {brand_name}")
    brand = find_brand(brand_name)
    if not brand:
        log.error(f"Brand '{brand_name}' not found on GSMArena.")
        sys.exit(1)

    log.info(f"Found: {brand['name']}  ({brand['phone_count']} phones total)")
    log.info(f"Fetching phone list (limit={limit or 'all'}) ...")
    phones = get_phones_for_brand(brand["url"], limit=limit)
    print_phone_list(phones, brand["name"])

    path = save_to_json(
        {"brand": brand, "phones": phones},
        label=brand["name"],
    )
    log.info(f"Saved to {path}")


def cmd_phone(phone_name: str):
    log.info(f"Searching: {phone_name}")
    match = search_phone(phone_name)
    if not match:
        log.error(f"No result found for '{phone_name}'.")
        sys.exit(1)

    log.info(f"Found: {match['name']}")
    log.info("Fetching specs ...")
    specs = get_phone_specs(match["url"])
    if not specs:
        log.error("Could not fetch specs.")
        sys.exit(1)

    print_specs(specs)
    path = save_to_json(specs, label=match["name"])
    log.info(f"Saved to {path}")


def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="GSMArena scraper — search by brand or phone name",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--brand", metavar="BRAND", help='Brand name  e.g. "Samsung"')
    group.add_argument("--phone", metavar="PHONE", help='Phone name  e.g. "Apple iPhone 17 Pro"')
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Max phones to show for --brand (default 20, 0 = all pages)",
    )
    args = parser.parse_args()

    if args.brand:
        cmd_brand(args.brand, args.limit)
    elif args.phone:
        cmd_phone(args.phone)


if __name__ == "__main__":
    main()
