

import logging
import sys
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "trading_bot.log"

_configured = False


def get_logger(name: str = "trading_bot") -> logging.Logger:
  
    global _configured

    logger = logging.getLogger(name)

    if _configured:
        return logger

    logger.setLevel(logging.DEBUG)

    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(file_fmt)

    console_fmt = logging.Formatter(fmt="%(levelname)-8s %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(console_fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    _configured = True
    return logger
