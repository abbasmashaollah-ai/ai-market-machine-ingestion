from __future__ import annotations

import io
import json
import ast
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

from scripts.dry_run_sector_etf_ohlcv_handoff import SECTOR_ETF_UNIVERSE, main


def test_default_dry_run_emits_safe_summary() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["dry_run"] is True
    assert payload["universe_count"] == 12
    assert payload["records_generated"] == 12
    assert payload["symbols_ready"] == list(SECTOR_ETF_UNIVERSE)
    assert payload["symbols_missing"] == []
    assert payload["validation_status"] == "PASS"
    assert payload["certification_status"] == "FIXTURE_ONLY"
    assert payload["production_eligible"] is False
    assert payload["fixture_only"] is True
    assert payload["db_write_attempted"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert len(payload["idempotency_key_prefixes"]) == 12
    assert all(len(prefix) <= 12 for prefix in payload["idempotency_key_prefixes"])


def test_output_file_writes_safe_summary_only(tmp_path: Path) -> None:
    output_file = tmp_path / "dry_runs" / "sector_etf_ohlcv_handoff.json"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--output-file", str(output_file)])

    assert exit_code == 0
    stdout_payload = json.loads(buffer.getvalue())
    file_payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert file_payload["production_eligible"] is False
    assert file_payload["fixture_only"] is True


def test_cli_runs_as_subprocess_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/dry_run_sector_etf_ohlcv_handoff.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["universe_count"] == 12
    assert payload["records_generated"] == 12
    assert payload["production_eligible"] is False


def test_source_scan_confirms_no_writer_db_vendor_live_or_scheduler_imports() -> None:
    source = Path("scripts/dry_run_sector_etf_ohlcv_handoff.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())

    assert "app.vendor_flat_files.ohlcv_handoff_builder" in import_names
    for forbidden in [
        "requests",
        "httpx",
        "market_feature_bundle_db_adapter",
        "database",
        "session",
        "writer",
    ]:
        assert forbidden not in source


def test_no_secrets_or_full_keys_in_output() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main([])

    assert exit_code == 0
    text = buffer.getvalue().lower()
    for forbidden in ["secret", "token", "credential", "api_key", "apikey", "raw_vendor"]:
        assert forbidden not in text
