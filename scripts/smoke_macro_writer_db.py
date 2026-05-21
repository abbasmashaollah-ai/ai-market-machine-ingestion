from __future__ import annotations

import argparse
import os
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from urllib.parse import urlparse

from app.models.normalized import NormalizedMacroObservation
from app.writers.macro_writer import MacroWriter


SMOKE_SERIES_ID = "INGESTION_SMOKE_TEST"
SMOKE_SOURCE = "FRED"
SMOKE_TIMESTAMP = datetime(2000, 1, 1, tzinfo=timezone.utc)
SMOKE_VALUE = 1.0


def load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


@dataclass(frozen=True)
class SmokeCheckResult:
    database_url_present: bool
    confirm_write: bool
    would_write: bool
    status: str
    message: str
    written_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    error_type: str | None = None
    sanitized_error_message: str | None = None


def build_smoke_records() -> list[NormalizedMacroObservation]:
    return [
        NormalizedMacroObservation(
            symbol=SMOKE_SERIES_ID,
            symbol_id=SMOKE_SERIES_ID,
            timestamp=SMOKE_TIMESTAMP,
            value=SMOKE_VALUE,
            vendor="FRED",
            source=SMOKE_SOURCE,
        )
    ]


def _is_postgres_url(database_url: str) -> bool:
    scheme = urlparse(database_url).scheme.lower()
    return scheme in {"postgresql", "postgres"}


def _load_postgres_connect() -> Callable[[str], object]:
    try:
        from psycopg import connect as psycopg_connect  # type: ignore
    except ImportError:
        try:
            from psycopg2 import connect as psycopg_connect  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency specific
            raise RuntimeError(
                "PostgreSQL smoke writes require psycopg or psycopg2 to be installed."
            ) from exc
    return psycopg_connect


def _open_connection(database_url: str):
    if not _is_postgres_url(database_url):
        raise RuntimeError(
            "Unsupported URL scheme for smoke test; use postgresql:// or postgres://"
        )
    return _load_postgres_connect()(database_url)


def _sanitize_error_message(message: str) -> str:
    sanitized = message
    sanitized = re.sub(r"(?i)sqlalchemy(?:\.engine)?(?:\.[A-Za-z_]+)*\.[A-Za-z_]+:.*", "sqlalchemy driver error: <redacted>", sanitized)
    sanitized = re.sub(r"(?i)(postgres(?:ql)?://)([^\s:@/]+)(?::([^\s@/]+))?@", r"\1<redacted>@", sanitized)
    sanitized = re.sub(r"(?i)(password|passwd|pwd|token|secret|key)=([^\s&]+)", r"\1=<redacted>", sanitized)
    sanitized = re.sub(r"(?i)DATABASE_URL", "database connection", sanitized)
    return sanitized


def run_smoke_check(*, confirm_write: bool) -> SmokeCheckResult:
    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return SmokeCheckResult(
            database_url_present=False,
            confirm_write=confirm_write,
            would_write=False,
            status="dry",
            message="DATABASE_URL is not set",
        )
    if not confirm_write:
        return SmokeCheckResult(
            database_url_present=True,
            confirm_write=False,
            would_write=False,
            status="dry",
            message="Dry check only. Re-run with --confirm-write to execute a tiny smoke write.",
        )

    try:
        with closing(_open_connection(database_url)) as connection:
            writer = MacroWriter(connection)
            result = writer.write(build_smoke_records())
    except Exception as exc:
        return SmokeCheckResult(
            database_url_present=True,
            confirm_write=True,
            would_write=False,
            status="failed",
            message=_sanitize_error_message(str(exc)),
            error_type=exc.__class__.__name__,
            sanitized_error_message=_sanitize_error_message(str(exc)),
        )

    status = result.status.value
    return SmokeCheckResult(
        database_url_present=True,
        confirm_write=True,
        would_write=True,
        status=status,
        message=f"Smoke write completed status={status}",
        written_count=result.written_count,
        skipped_count=result.skipped_count,
        failed_count=result.failed_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual smoke test for MacroWriter against a real database.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write the tiny smoke row.")
    args = parser.parse_args()

    result = run_smoke_check(confirm_write=args.confirm_write)
    print(
        f"status={result.status} "
        f"written={result.written_count} skipped={result.skipped_count} failed={result.failed_count}"
    )
    print(f"error_type={result.error_type}")
    print(f"sanitized_error_message={result.sanitized_error_message}")
    print(f"smoke_series_id={SMOKE_SERIES_ID}")
    print(f"smoke_source={SMOKE_SOURCE}")
    print(f"smoke_date=2000-01-01")
    print(f"confirm_write={result.confirm_write}")
    print(f"would_write={result.would_write}")
    return 0 if result.database_url_present else 1


if __name__ == "__main__":
    raise SystemExit(main())
