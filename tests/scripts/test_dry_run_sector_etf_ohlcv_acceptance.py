from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.dry_run_sector_etf_ohlcv_acceptance as cli



def test_cli_fixture_only_dry_run_emits_safe_summary() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["records_received"] == 12
    assert payload["accepted_count"] == 0
    assert payload["rejected_count"] == 12
    assert payload["production_write_attempted"] is False
    assert payload["db_write_attempted"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert len(payload["idempotency_key_prefixes"]) == 12


def test_cli_approved_candidate_mode_accepts_in_decision_form() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(["--approved-candidate-test-mode"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["records_received"] == 12
    assert payload["accepted_count"] == 12
    assert payload["rejected_count"] == 0
    assert payload["symbols_accepted"][0] == "SPY"


def test_cli_runs_as_subprocess_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/dry_run_sector_etf_ohlcv_acceptance.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["records_received"] == 12
    assert payload["db_write_attempted"] is False


def test_source_scan_confirms_no_db_vendor_or_scheduler_imports() -> None:
    source = Path("scripts/dry_run_sector_etf_ohlcv_acceptance.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())
    for forbidden in ["sqlalchemy", "requests", "httpx"]:
        assert forbidden not in import_names
    assert "sessionmaker" not in source
    assert "create_engine" not in source
    assert "database_url" not in source
    assert "amm_test_database_url" not in source
    assert "vendor_call_attempted" in source
    assert "scheduler_activation_attempted" in source
