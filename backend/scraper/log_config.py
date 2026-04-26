import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    log_dir = Path(__file__).parent.parent / "log"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    fmt = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    datefmt = "%H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)

    root.setLevel(logging.DEBUG)
    root.addHandler(fh)
    root.addHandler(sh)
