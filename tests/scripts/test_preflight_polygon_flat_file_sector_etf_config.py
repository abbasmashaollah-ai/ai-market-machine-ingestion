from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.preflight_polygon_flat_file_sector_etf_config as cli


def test_default_preflight_is_read_only_and_does_not_call_vendor_services() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["preflight_only"] is True
    assert payload["polygon_flat_file_source_selected"] is True
    assert payload["vendor_call_attempted"] is False
    assert payload["remote_bucket_list_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["export_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["ingestion_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["production_mutation_attempted"] is False
    assert payload["production_eligible_generation_authorized"] is False
    assert payload["synthetic_forbidden"] is True
    assert payload["fixture_only_forbidden"] is True
    assert payload["credentials_printed"] is False
    assert payload["flat_file_adapter_detected"] is True
    assert payload["benchmark_symbol"] == "SPY"
    assert payload["sector_etf_universe_detected"] is True
    assert "XLB" in payload["required_sector_symbols"]
    assert "XLY" in payload["required_sector_symbols"]
    assert payload["sector_etf_universe_symbols"][0] == "SPY"


def test_missing_config_names_are_reported_by_name_only(monkeypatch) -> None:
    for name in cli.REQUIRED_CONFIG_NAMES:
        monkeypatch.delenv(name, raising=False)
    payload = cli._safe_payload()
    assert payload["credentials_present"] is False
    assert payload["missing_config_names"] == list(cli.REQUIRED_CONFIG_NAMES)
    text = json.dumps(payload, sort_keys=True)
    for secret_needle in ["postgresql", "apikey", "bucket-value", "prefix-value", "http://", "https://"]:
        assert secret_needle not in text.lower()


def test_local_parser_and_handoff_builder_are_detected() -> None:
    payload = cli._safe_payload()
    assert payload["local_parser_detected"] is True
    assert payload["handoff_builder_detected"] is True


def test_source_scan_blocks_network_download_export_db_and_scheduler_usage() -> None:
    source = Path("scripts/preflight_polygon_flat_file_sector_etf_config.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())
    for forbidden in ["requests", "httpx", "sqlalchemy", "boto3", "app.api", "app.scheduler.jobs", "alembic"]:
        assert forbidden not in import_names
    assert "polygon_flat_file_adapter" in source
    assert "vendor_call_attempted" in source
    assert "remote_bucket_list_attempted" in source
    assert "download_attempted" in source
    assert "export_attempted" in source
    assert "db_write_attempted" in source
    assert "ingestion_attempted" in source
    assert "scheduler_activation_attempted" in source
    assert "production_mutation_attempted" in source
    assert "preflight_only" in source


def test_help_mentions_output_file_only() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/preflight_polygon_flat_file_sector_etf_config.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--output-file" in result.stdout


def test_output_includes_expected_symbols_and_spy_benchmark() -> None:
    payload = cli._safe_payload()
    assert payload["benchmark_symbol"] == "SPY"
    assert set(payload["required_sector_symbols"]) == {"XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"}
    assert set(payload["sector_etf_universe_symbols"]) == {"SPY", "XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"}
