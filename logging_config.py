from __future__ import annotations

import logging
import os

from pythonjsonlogger import json


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    formatter = json.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        json_ensure_ascii=False,
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
