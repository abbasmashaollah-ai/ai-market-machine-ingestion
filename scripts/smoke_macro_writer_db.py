from __future__ import annotations

import argparse
import os
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

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
    message: str


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


def _open_connection(database_url: str):
    if database_url.startswith("sqlite:///"):
        import sqlite3

        path = database_url.removeprefix("sqlite:///")
        return sqlite3.connect(path)
    raise RuntimeError("DATABASE_URL must reference a supported local test database for this smoke script")


def run_smoke_check(*, confirm_write: bool) -> SmokeCheckResult:
    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return SmokeCheckResult(
            database_url_present=False,
            confirm_write=confirm_write,
            would_write=False,
            message="DATABASE_URL is not set",
        )
    if not confirm_write:
        return SmokeCheckResult(
            database_url_present=True,
            confirm_write=False,
            would_write=False,
            message="Dry check only. Re-run with --confirm-write to execute a tiny smoke write.",
        )

    with closing(_open_connection(database_url)) as connection:
        writer = MacroWriter(connection)
        result = writer.write(build_smoke_records())
        return SmokeCheckResult(
            database_url_present=True,
            confirm_write=True,
            would_write=True,
            message=(
                f"Smoke write completed status={result.status.value} "
                f"written={result.written_count} skipped={result.skipped_count} failed={result.failed_count}"
            ),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual smoke test for MacroWriter against a real database.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write the tiny smoke row.")
    args = parser.parse_args()

    result = run_smoke_check(confirm_write=args.confirm_write)
    print(result.message)
    print(f"smoke_series_id={SMOKE_SERIES_ID}")
    print(f"smoke_source={SMOKE_SOURCE}")
    print(f"smoke_date=2000-01-01")
    print(f"confirm_write={result.confirm_write}")
    print(f"would_write={result.would_write}")
    return 0 if result.database_url_present else 1


if __name__ == "__main__":
    raise SystemExit(main())
