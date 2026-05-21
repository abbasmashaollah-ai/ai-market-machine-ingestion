from __future__ import annotations

import logging
from typing import Any


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for key in ("run_id", "vendor", "dataset", "symbol", "timeframe"):
            if not hasattr(record, key):
                setattr(record, key, None)
        return True


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s run_id=%(run_id)s vendor=%(vendor)s dataset=%(dataset)s symbol=%(symbol)s timeframe=%(timeframe)s %(message)s",
    )
    logging.getLogger().addFilter(ContextFilter())


def get_logger(name: str, **context: Any) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger(name), context)
