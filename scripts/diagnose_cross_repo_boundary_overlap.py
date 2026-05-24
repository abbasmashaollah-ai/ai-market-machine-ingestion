from __future__ import annotations

import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _relative_matches(patterns: tuple[str, ...]) -> list[str]:
    matches: set[str] = set()
    for pattern in patterns:
        for path in REPO_ROOT.glob(pattern):
            if path.exists():
                matches.add(path.relative_to(REPO_ROOT).as_posix())
    return sorted(matches)


def _format_matches(paths: list[str]) -> str:
    return ",".join(paths) if paths else "none"


def _print_category(name: str, patterns: tuple[str, ...]) -> None:
    paths = _relative_matches(patterns)
    print(f"{name}={_format_matches(paths)}")


def _packaging_issue(name: str, path: Path) -> None:
    print(f"{name}={str(path.exists()).lower()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit boundary overlap between ingestion and data ownership.")
    parser.parse_args()

    print("audit_status=read_only")
    print("cross_repo_boundary=ai-market-machine-data_vs_ai-market-machine-ingestion")
    print("data_repo_ownership=schema,migrations,canonical_read_apis,grafana_read_models")
    print("ingestion_repo_ownership=vendor_fetching,daily_runners,backfills,flat_files,websocket,scheduler_execution")

    _print_category("data_owned_schema", ("app/models/**", "app/state/data_*"))
    _print_category("data_owned_read_api", ("app/api/**",))
    _print_category("data_owned_grafana_monitoring", ("app/monitoring/**",))
    _print_category(
        "ingestion_overlap_runtime",
        (
            "app/ingestion/**",
            "scripts/run_daily_ingestion.py",
            "scripts/run_polygon_ohlcv_daily_update.py",
            "scripts/run_polygon_ohlcv_chunked_backfill.py",
        ),
    )
    _print_category(
        "ingestion_overlap_scheduler",
        (
            "app/ingestion/daily/**",
            "scripts/start_scheduler.py",
            "scripts/run_polygon_ohlcv_scheduler_cycle.py",
            "scripts/verify_polygon_scheduler_disabled.py",
        ),
    )
    _print_category("ingestion_overlap_vendor_clients", ("app/ingestion/manual/**", "app/vendors/**"))
    _print_category("ingestion_overlap_mutation_endpoints", ("app/api/health.py", "app/api/**"))
    _print_category("legacy_or_deprecate", ("scripts/run_daily_ingestion.py", "scripts/start_scheduler.py", "logs/**"))

    print("packaging_hygiene_issues=")
    _packaging_issue(".env", REPO_ROOT / ".env")
    _packaging_issue(".venv", REPO_ROOT / ".venv")
    _packaging_issue(".git", REPO_ROOT / ".git")
    _packaging_issue("__pycache__", REPO_ROOT / "__pycache__")
    _packaging_issue(".pytest_cache", REPO_ROOT / ".pytest_cache")
    _packaging_issue("logs", REPO_ROOT / "logs")

    print("boundary_audit_status=diagnostic_only")
    print("production_switch_enabled=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
