import logging

log = logging.getLogger("scraper.display")


def print_phone_list(phones: list[dict], brand_name: str):
    log.info(f"Displaying {len(phones)} phones for brand '{brand_name}'")
    print(f"\n{'=' * 60}")
    print(f"  {brand_name}  —  {len(phones)} phones")
    print(f"{'=' * 60}")
    for i, p in enumerate(phones, 1):
        print(f"  {i:>3}. {p['name']}")
        print(f"        {p['url']}")
    print()


def print_specs(phone: dict):
    name = phone.get("name", "Unknown")
    log.info(f"Displaying specs for '{name}' ({len(phone.get('specs', {}))} fields)")
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")
    if phone.get("image_url"):
        print(f"  Image : {phone['image_url']}")
    print()
    for label, value in phone.get("specs", {}).items():
        print(f"  {label:<38} {value}")
    print()
