from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date

from app.core.exceptions import ConfigError


def _parse_int(name: str, default: int | None = None) -> int | None:
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"Invalid integer for {name}") from exc


def _parse_date(name: str) -> date | None:
    raw = os.getenv(name)
    if raw in (None, ""):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ConfigError(f"Invalid date for {name}") from exc


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    POLYGON_API_KEY: str | None
    FRED_API_KEY: str | None
    LOG_LEVEL: str
    ENVIRONMENT: str
    INGESTION_BATCH_SIZE: int
    INGESTION_MAX_RETRIES: int
    INGESTION_RATE_LIMIT_PER_MINUTE: int | None
    BACKFILL_START_DATE: date | None
    BACKFILL_END_DATE: date | None
    RAW_DATA_BUCKET: str | None
    ALERT_WEBHOOK_URL: str | None


def load_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ConfigError("DATABASE_URL is required")

    return Settings(
        DATABASE_URL=database_url,
        POLYGON_API_KEY=os.getenv("POLYGON_API_KEY") or None,
        FRED_API_KEY=os.getenv("FRED_API_KEY") or None,
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        ENVIRONMENT=os.getenv("ENVIRONMENT", "local"),
        INGESTION_BATCH_SIZE=_parse_int("INGESTION_BATCH_SIZE", 1000) or 1000,
        INGESTION_MAX_RETRIES=_parse_int("INGESTION_MAX_RETRIES", 3) or 3,
        INGESTION_RATE_LIMIT_PER_MINUTE=_parse_int("INGESTION_RATE_LIMIT_PER_MINUTE"),
        BACKFILL_START_DATE=_parse_date("BACKFILL_START_DATE"),
        BACKFILL_END_DATE=_parse_date("BACKFILL_END_DATE"),
        RAW_DATA_BUCKET=os.getenv("RAW_DATA_BUCKET") or None,
        ALERT_WEBHOOK_URL=os.getenv("ALERT_WEBHOOK_URL") or None,
    )
