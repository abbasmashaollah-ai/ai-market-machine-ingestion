from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.persist_fred_macro import load_local_env_if_available


def _require_database_url(confirm_write: bool, check_existing: bool) -> str | None:
    database_url = os.getenv("DATABASE_URL")
    if (confirm_write or check_existing) and not database_url:
        raise RuntimeError("DATABASE_URL is required when confirm-write or check-existing is requested")
    return database_url


def _assert_text_not_present(path: Path, needles: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    violations = [needle for needle in needles if needle.lower() in lowered]
    return violations


def _check_inventory() -> bool:
    from scripts import verify_manual_ingestion_commands as inventory

    return "scripts.dry_run_symbol_master_ingestion" in inventory.MODULES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight symbol master manual operations safely.")
    parser.add_argument("--confirm-write", action="store_true", help="Require the confirmed-write environment contract.")
    parser.add_argument("--check-existing", action="store_true", help="Require DATABASE_URL and verify schema access paths.")
    args = parser.parse_args(argv)

    load_local_env_if_available()
    database_url = _require_database_url(args.confirm_write, args.check_existing)

    inventory_ok = _check_inventory()
    writer_doc_exists = Path("docs/symbol_master_writer.md").exists()
    foundation_doc_exists = Path("docs/symbol_master_ingestion_foundation.md").exists()
    writer_source = Path("app/writers/symbol_master_writer.py")
    runner_source = Path("scripts/dry_run_symbol_master_ingestion.py")

    forbidden_violations = []
    forbidden_violations.extend(_assert_text_not_present(writer_source, ("ai_market_machine_data", "fastapi", "apirouter", "requests", "httpx", "alembic")))
    forbidden_violations.extend(_assert_text_not_present(runner_source, ("ai_market_machine_data", "fastapi", "apirouter", "requests", "httpx", "alembic")))

    data_contract_refs_ok = "symbol_master" in writer_source.read_text(encoding="utf-8").lower() and "app.database" not in writer_source.read_text(encoding="utf-8")
    status = "PASS"
    blockers: list[str] = []
    warnings: list[str] = []

    if not inventory_ok:
        status = "FAIL"
        blockers.append("manual command inventory missing symbol master dry-run runner")
    if not writer_doc_exists or not foundation_doc_exists:
        status = "FAIL"
        blockers.append("symbol master docs missing")
    if forbidden_violations:
        status = "FAIL"
        blockers.extend(f"forbidden_import:{item}" for item in forbidden_violations)
    if not data_contract_refs_ok:
        status = "FAIL"
        blockers.append("writer source references data internals instead of table contract")

    if database_url is None and not (args.confirm_write or args.check_existing):
        warnings.append("DATABASE_URL not required for dry-run preflight")
    if database_url is None and (args.confirm_write or args.check_existing):
        status = "FAIL"
        blockers.append("DATABASE_URL required for confirm-write/check-existing")

    if status == "PASS" and not writer_doc_exists:
        status = "WARN"
        warnings.append("writer documentation missing")

    print(
        f"symbol_master_preflight_status={status} "
        f"inventory_ok={inventory_ok} "
        f"writer_doc_exists={writer_doc_exists} "
        f"foundation_doc_exists={foundation_doc_exists} "
        f"confirm_write={args.confirm_write} "
        f"check_existing={args.check_existing} "
        f"database_url_required={bool(args.confirm_write or args.check_existing)} "
        f"database_url_present={database_url is not None} "
        f"forbidden_imports_ok={not forbidden_violations} "
        f"data_contract_refs_ok={data_contract_refs_ok} "
        f"blockers={blockers} "
        f"warnings={warnings}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
