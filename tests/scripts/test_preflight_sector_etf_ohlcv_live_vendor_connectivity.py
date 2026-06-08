from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from dataclasses import asdict
from pathlib import Path

import scripts.preflight_sector_etf_ohlcv_live_vendor_connectivity as cli


def test_default_run_does_not_call_vendors_or_download() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["preflight_only"] is True
    assert payload["live_connectivity_enabled"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["historical_download_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False
    assert payload["approved_vendor_required"] is True
    assert payload["synthetic_forbidden"] is True
    assert payload["fixture_only_forbidden"] is True
    assert payload["production_handoff_generation_authorized"] is False
    assert payload["credentials_printed"] is False
    assert payload["historical_data_downloaded"] is False
    assert payload["handoff_artifact_exported"] is False
    assert "SPY" in payload["symbols_expected"]
    assert "XLB" in payload["symbols_probe_scope"]


def test_live_flag_changes_status_but_still_no_download_or_export(monkeypatch) -> None:
    monkeypatch.setenv("POLYGON_API_KEY", "test-key")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(["--enable-live-connectivity"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["live_connectivity_enabled"] is True
    assert payload["vendor_call_attempted"] is True
    assert payload["historical_download_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["credentials_printed"] is False


def test_source_scan_blocks_history_download_export_db_scheduler_and_mutation_usage() -> None:
    source = Path("scripts/preflight_sector_etf_ohlcv_live_vendor_connectivity.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())
    for forbidden in ["sqlalchemy", "requests", "httpx", "app.api", "app.scheduler.jobs", "alembic"]:
        assert forbidden not in import_names
    assert "session" not in source
    assert "create_engine" not in source
    assert "database_url" not in source
    assert "amm_test_database_url" not in source
    assert "vendor_call_attempted" in source
    assert "historical_download_attempted" in source
    assert "export_attempted" in source
    assert "db_write_attempted" in source
    assert "ingestion_attempted" in source
    assert "scheduler_activation_attempted" in source
    assert "production_mutation_attempted" in source
    assert "preflight_only" in source
    assert "credentials_printed" in source


def test_no_secrets_or_database_urls_are_printed() -> None:
    payload = cli._safe_payload(enabled=False, production_vendor_url=None)
    text = json.dumps(asdict(payload), sort_keys=True)
    assert "apikey" not in text.lower()
    assert "secret" not in text.lower()
    assert "password" not in text.lower()
    assert "postgresql" not in text.lower()
    assert "database_url" not in text.lower()


def test_help_mentions_live_connectivity_flag() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_sector_etf_ohlcv_live_vendor_connectivity.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--enable-live-connectivity" in result.stdout
