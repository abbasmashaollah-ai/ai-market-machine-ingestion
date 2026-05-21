from __future__ import annotations

from dataclasses import dataclass

from app.core.config import load_settings


@dataclass(frozen=True)
class DatabaseConfig:
    url: str


def get_database_config() -> DatabaseConfig:
    settings = load_settings()
    return DatabaseConfig(url=settings.DATABASE_URL)
