from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class HealthStatus:
    service: str
    ok: bool
    app_imports_ok: bool
    config_shape_ok: bool
    database_url_present: bool
    database_url_valid: bool | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_database_url(database_url: str | None) -> tuple[bool, bool | None, str | None]:
    if not database_url:
        return False, None, None

    parsed = urlparse(database_url)
    if not parsed.scheme or not parsed.netloc:
        return False, False, "DATABASE_URL is present but not a valid URL"
    return True, True, None


def check_runtime_health() -> HealthStatus:
    app_imports_ok = True
    config_shape_ok = True
    message = None

    try:
        import app  # noqa: F401
        from app.core.config import Settings  # noqa: F401
        from app.core.runtime import RuntimeContext  # noqa: F401
    except Exception as exc:  # pragma: no cover - defensive guard
        return HealthStatus(
            service="ai-market-machine-ingestion",
            ok=False,
            app_imports_ok=False,
            config_shape_ok=False,
            database_url_present=False,
            database_url_valid=None,
            message=f"Import failure: {exc}",
        )

    expected_fields = {
        "DATABASE_URL",
        "POLYGON_API_KEY",
        "FRED_API_KEY",
        "LOG_LEVEL",
        "ENVIRONMENT",
        "INGESTION_BATCH_SIZE",
        "INGESTION_MAX_RETRIES",
        "INGESTION_RATE_LIMIT_PER_MINUTE",
        "BACKFILL_START_DATE",
        "BACKFILL_END_DATE",
        "RAW_DATA_BUCKET",
        "ALERT_WEBHOOK_URL",
    }

    from app.core.config import Settings

    config_shape_ok = set(Settings.__annotations__) == expected_fields

    import os

    database_url = os.getenv("DATABASE_URL")
    database_url_present = bool(database_url)
    _, database_url_valid, url_message = _validate_database_url(database_url)
    if url_message:
        message = url_message

    ok = app_imports_ok and config_shape_ok and (database_url_valid is not False)
    return HealthStatus(
        service="ai-market-machine-ingestion",
        ok=ok,
        app_imports_ok=app_imports_ok,
        config_shape_ok=config_shape_ok,
        database_url_present=database_url_present,
        database_url_valid=database_url_valid,
        message=message,
    )


def main() -> int:
    status = check_runtime_health()
    print(status.to_dict())
    return 0 if status.ok else 1
