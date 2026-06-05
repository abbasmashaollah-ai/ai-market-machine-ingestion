from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys

from scripts.run_market_feature_bundle_production_pilot_dry_run import main


def test_production_pilot_dry_run_prints_safe_report() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--observation-date", "2026-01-15", "--timestamp", "2026-01-15T18:00:00Z"])

    assert exit_code == 0
    report = json.loads(buffer.getvalue())
    assert report["dry_run"] is True
    assert report["universe"] == "SPY"
    assert report["dataset_version"] == "production_pilot.v1"
    assert report["idempotency_key_prefix"]
    assert len(report["idempotency_key_prefix"]) <= 12
    assert report["write_status"] == "DRY_RUN_READY"
    assert report["observability_event"]["idempotency_key_prefix"] == report["idempotency_key_prefix"]
    assert "idempotency_key" not in report["observability_event"] or report["observability_event"].get("idempotency_key") is None
    assert report["preserve_policy"] == "PRESERVE_FIRST_PRODUCTION_ROW"
    assert report["scheduler_enabled"] is False
    assert report["backfill_enabled"] is False
    assert report["ai_machine_touched"] is False
    assert report["target_table"] == "market_feature_bundle_snapshots"
    assert report["target_repo"] == "ai-market-machine-data"
    assert report["validation_status"]
    assert report["certification_status"]
    assert "placeholder-idempotency-key" not in buffer.getvalue()


def test_production_pilot_dry_run_runs_as_subprocess_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_market_feature_bundle_production_pilot_dry_run.py", "--observation-date", "2026-01-15"],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    assert report["dry_run"] is True
    assert report["universe"] == "SPY"
    assert report["dataset_version"] == "production_pilot.v1"
    assert report["scheduler_enabled"] is False
    assert report["backfill_enabled"] is False
    assert report["ai_machine_touched"] is False


def test_production_pilot_dry_run_source_has_no_forbidden_imports() -> None:
    source = Path("scripts/run_market_feature_bundle_production_pilot_dry_run.py").read_text(encoding="utf-8").lower()
    for marker in [
        "sqlalchemy",
        "app.database",
        "database_url",
        "requests",
        "httpx",
        "aiohttp",
        "import scheduler",
        "from scheduler",
        "scheduler.",
        "vendor",
        "production write",
    ]:
        assert marker not in source
