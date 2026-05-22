from __future__ import annotations

import importlib
import os

from app.core.health import _validate_database_url


COMMAND_MODULES = (
    "scripts.persist_fred_macro_incremental",
    "scripts.dry_run_fred_macro_incremental",
    "scripts.preview_fred_macro_incremental",
)


def _import_manual_commands() -> list[str]:
    imported: list[str] = []
    for module_name in COMMAND_MODULES:
        module = importlib.import_module(module_name)
        if not callable(getattr(module, "main", None)):
            raise RuntimeError(f"{module_name} does not expose a callable main()")
        imported.append(module_name)
    return imported


def main() -> int:
    imported = _import_manual_commands()
    fred_api_key_present = bool(os.getenv("FRED_API_KEY"))
    database_url = os.getenv("DATABASE_URL")
    database_url_present = bool(database_url)
    _, database_url_valid, _ = _validate_database_url(database_url)

    dry_run_ready = fred_api_key_present and len(imported) == len(COMMAND_MODULES)
    confirmed_write_ready = fred_api_key_present and database_url_present and bool(database_url_valid)
    missing = []
    if not fred_api_key_present:
        missing.append("FRED_API_KEY")
    if not database_url_present:
        missing.append("DATABASE_URL")

    print(f"dry_run_ready={str(dry_run_ready).lower()}")
    print(f"confirmed_write_ready={str(confirmed_write_ready).lower()}")
    print(f"missing={missing}")
    print(f"imported={imported}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

