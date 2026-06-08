from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preflight_sector_etf_ohlcv_vendor_provenance as cli


def test_default_cli_is_read_only_and_never_calls_vendors() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["preflight_only"] is True
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False
    assert payload["live_connectivity_enabled"] is False
    assert payload["approved_vendor_required"] is True
    assert payload["synthetic_forbidden"] is True
    assert payload["fixture_only_forbidden"] is True
    assert payload["production_handoff_generation_authorized"] is False
    assert "XLB" in payload["symbols_missing_in_production_context"]
    assert "SPY" in payload["symbols_expected"]


def test_output_contains_required_handoff_and_provenance_fields() -> None:
    payload = cli._safe_payload()
    for field in [
        "symbol",
        "observation_date or timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "timeframe",
        "adjusted",
        "source/vendor",
        "dataset_version",
        "schema_version",
        "validation_status",
        "certification_status",
        "lineage_id",
        "checksum or source_file_sha256",
        "deterministic idempotency_key",
    ]:
        assert field in payload["required_handoff_fields"]
    for field in [
        "approved vendor/source attribution",
        "lineage preserved",
        "checksum preserved",
        "validation_status = PASS",
        "certification_status not equal to FIXTURE_ONLY",
    ]:
        assert field in payload["required_provenance_fields"]


def test_source_scan_confirms_no_vendor_download_export_db_scheduler_or_live_ingestion_usage() -> None:
    source = Path("scripts/preflight_sector_etf_ohlcv_vendor_provenance.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())
    for forbidden in ["requests", "httpx", "sqlalchemy"]:
        assert forbidden not in import_names
    assert "session" not in source
    assert "create_engine" not in source
    assert "database_url" not in source
    assert "amm_test_database_url" not in source
    assert "vendor_call_attempted" in source
    assert "download_attempted" in source
    assert "export_attempted" in source
    assert "db_write_attempted" in source
    assert "ingestion_attempted" in source
    assert "scheduler_activation_attempted" in source
    assert "production_mutation_attempted" in source
    assert "preflight_only" in source


def test_docs_mention_required_guardrails_and_next_step() -> None:
    text = Path("docs/sector_etf_ohlcv_vendor_provenance_preflight.md").read_text(encoding="utf-8")
    assert "no vendor calls by default" in text
    assert "no downloads" in text
    assert "no exports" in text
    assert "no DB writes" in text
    assert "no live ingestion" in text
    assert "no scheduler activation" in text
    assert "approved vendor-produced records only" in text
    assert "fixture-only records" in text
    assert "SPY is the benchmark" in text
    assert "XLB" in text and "XLY" in text
    assert "next allowed implementation step" in text
    assert "not production export" in text


def test_help_mentions_live_connectivity_flag() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_sector_etf_ohlcv_vendor_provenance.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--live-connectivity" in result.stdout
