import json
import os
import re
from datetime import datetime


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "_", text)
    return re.sub(r"-+", "_", text)


def save_to_json(data: dict | list, label: str) -> str:
    """
    Save scraped data to output/<label>_<timestamp>.json.
    Returns the file path.
    """
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/{_slugify(label)}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filename
