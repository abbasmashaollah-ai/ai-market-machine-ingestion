from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import scripts.preflight_polygon_stock_day_agg_ingestion_production_readiness as cli


def _payload(monkeypatch, *, missing: set[str] | None = None, tracked: bool = False, db: bool = False, scheduler: bool = False, data_repo: bool = False) -> dict[str, object]:
    missing = missing or set()

    def exists(paths: tuple[str, ...]) -> list[str]:
        return [path for path in paths if path not in missing]

    monkeypatch.setattr(cli, "_exists", exists)
    monkeypatch.setattr(cli, "_scan_for_blockers", lambda: {
        "production_db_write_detected": db,
        "scheduler_activation_detected": scheduler,
        "data_repo_mutation_detected": data_repo,
    })
    monkeypatch.setattr(cli, "_generated_artifact_flags", lambda: (tracked, False))
    return cli.build_payload()


def test_complete_evidence_returns_ready_for_operator_review(monkeypatch) -> None:
    payload = _payload(monkeypatch)
    assert payload["ingestion_readiness_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert payload["missing_scripts"] == []
    assert payload["missing_tests"] == []
    assert payload["missing_docs"] == []
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False


def test_missing_script_returns_evidence_incomplete(monkeypatch) -> None:
    payload = _payload(monkeypatch, missing={"scripts/inspect_polygon_stock_day_agg_quarantine_file.py"})
    assert payload["ingestion_readiness_status"] == "EVIDENCE_INCOMPLETE"
    assert "scripts/inspect_polygon_stock_day_agg_quarantine_file.py" in payload["missing_scripts"]


def test_tracked_generated_artifact_returns_blocked(monkeypatch) -> None:
    payload = _payload(monkeypatch, tracked=True)
    assert payload["generated_artifacts_tracked"] is True
    assert payload["ingestion_readiness_status"] == "BLOCKED"


def test_production_db_write_or_scheduler_activation_returns_blocked(monkeypatch) -> None:
    payload = _payload(monkeypatch, db=True, scheduler=True, data_repo=True)
    assert payload["production_db_write_detected"] is True
    assert payload["scheduler_activation_detected"] is True
    assert payload["data_repo_mutation_detected"] is True
    assert payload["ingestion_readiness_status"] == "BLOCKED"


def test_script_output_is_safe_json(monkeypatch) -> None:
    payload = _payload(monkeypatch)
    text = json.dumps(payload)
    assert "POLYGON_API_KEY" not in text
    assert "DATABASE_URL" not in text


def test_help_runs_without_side_effects() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_polygon_stock_day_agg_ingestion_production_readiness.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Read-only production readiness preflight" in result.stdout


def test_source_scan_blocks_mutation_and_vendor_calls() -> None:
    source = Path("scripts/preflight_polygon_stock_day_agg_ingestion_production_readiness.py").read_text(encoding="utf-8").lower()
    for forbidden in ("import requests", "import httpx", "import sqlalchemy", "import alembic", "get_object(", "download_file(", "put_object(", "polygon api key"):
        assert forbidden not in source
    for forbidden in ("requests.get(", "httpx.get(", ".to_sql(", "download_file(", "put_object("):
        assert forbidden not in source
