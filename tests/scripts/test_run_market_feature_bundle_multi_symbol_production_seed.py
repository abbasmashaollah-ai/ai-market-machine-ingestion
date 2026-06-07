from __future__ import annotations

import ast
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from scripts.run_market_feature_bundle_multi_symbol_production_seed import main


def test_default_run_is_dry_run_and_does_not_import_db_writer() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["dry_run"] is True
    assert payload["execute_requested"] is False
    assert payload["db_write_attempted"] is False
    assert payload["db_write_allowed"] is False
    assert payload["production_write_attempted"] is False
    assert payload["production_write_blocked"] is False
    assert payload["approval_env_present"] is False
    assert payload["db_url_env_present"] is False
    assert payload["symbols_requested"] == ["QQQ", "IWM", "DIA"]
    assert payload["symbols_ready"] == ["QQQ", "IWM", "DIA"]
    assert payload["symbols_blocked"] == []
    assert payload["validation_status"] == "PASS"
    assert payload["coverage_status"] == "COMPLETE"
    assert payload["quality_status"] == "PASS"
    assert payload["certification_status"] == "PRODUCTION_CANDIDATE"
    assert payload["idempotency_key_prefix"]["QQQ"]
    assert len(payload["idempotency_key_prefix"]["QQQ"]) <= 12


def test_execute_without_approval_env_blocks_write(monkeypatch) -> None:
    monkeypatch.delenv("AMM_PRODUCTION_PILOT_APPROVAL", raising=False)
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_DATABASE_URL", "postgresql://user:pass@localhost/test")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15", "--execute"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["execute_requested"] is True
    assert payload["db_write_attempted"] is False
    assert payload["db_write_allowed"] is False
    assert payload["production_write_attempted"] is False
    assert payload["production_write_blocked"] is True
    assert payload["approval_env_present"] is False


def test_execute_without_db_url_blocks_write(monkeypatch) -> None:
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_APPROVAL", "YES_APPROVED_MULTI_SYMBOL_WRITE")
    monkeypatch.delenv("AMM_PRODUCTION_PILOT_DATABASE_URL", raising=False)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15", "--execute"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["execute_requested"] is True
    assert payload["db_write_attempted"] is False
    assert payload["db_write_allowed"] is False
    assert payload["production_write_blocked"] is True
    assert payload["db_url_env_present"] is False


def test_execute_with_envs_still_blocks_as_scaffold(monkeypatch) -> None:
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_APPROVAL", "YES_APPROVED_MULTI_SYMBOL_WRITE")
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_DATABASE_URL", "postgresql://user:pass@localhost/test")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15", "--execute"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["execute_requested"] is True
    assert payload["db_write_allowed"] is True
    assert payload["db_write_attempted"] is False
    assert payload["production_write_attempted"] is False
    assert payload["production_write_blocked"] is True
    assert payload["execute_block_reason"] == "scaffold not yet approved for production writes"


def test_symbols_outside_allowed_universe_are_rejected() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "SPY,QQQ", "--observation-date", "2026-01-15"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["symbols_requested"] == ["SPY", "QQQ"]
    assert payload["symbols_blocked"] == ["SPY"]
    assert payload["per_symbol_status"]["SPY"]["status"] == "REJECTED"


def test_output_contains_no_full_db_url_token_secret_or_full_idempotency_key() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15"])

    assert exit_code == 0
    text = buffer.getvalue().lower()
    for forbidden in ["postgresql://", "token", "secret", "password=", "idempotency_key\":"]:
        assert forbidden not in text


def test_output_file_writes_local_summary_only(tmp_path: Path) -> None:
    output_file = tmp_path / "outputs" / "seed" / "summary.json"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15", "--output-file", str(output_file)])

    assert exit_code == 0
    stdout_payload = json.loads(buffer.getvalue())
    file_payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert file_payload["dry_run"] is True
    assert file_payload["db_write_attempted"] is False


def test_source_scan_confirms_no_vendor_or_live_api_or_scheduler_imports() -> None:
    source = Path("scripts/run_market_feature_bundle_multi_symbol_production_seed.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())

    for forbidden in [
        "requests",
        "httpx",
        "vendor",
        "provider",
        "scheduler",
        "engine",
        "session",
    ]:
        assert forbidden not in import_names


def test_scaffold_doc_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_production_seed_command.md")
    text = path.read_text(encoding="utf-8").lower()
    assert path.exists()
    for needle in [
        "dedicated multi-symbol production seed command scaffold",
        "default dry-run/no-write mode",
        "production write requires explicit second approval",
        "production write currently blocked unless implementation is explicitly approved",
        "qqq/iwm/dia",
        "no scheduler activation",
        "no broad backfill",
        "no automated recurring job",
        "no ai machine runtime wiring",
        "no db writes in tests",
        "no vendor calls",
        "no live api calls",
        "idempotency_key_prefix only",
        "safe json summary",
        "data api verification still required after any future write",
    ]:
        assert needle in text

