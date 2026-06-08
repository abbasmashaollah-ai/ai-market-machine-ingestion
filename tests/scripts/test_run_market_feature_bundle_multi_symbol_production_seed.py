from __future__ import annotations

import ast
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from scripts.run_market_feature_bundle_multi_symbol_production_seed import main


def test_default_run_is_dry_run_and_does_not_call_writer() -> None:
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
    assert payload["per_symbol_status"]["QQQ"]["status"] == "READY"
    assert payload["idempotency_key_prefix"]["QQQ"]
    assert len(payload["idempotency_key_prefix"]["QQQ"]) <= 12
    assert payload["symbols_written"] == []
    assert payload["symbols_noop"] == []
    assert payload["symbols_conflict"] == []
    assert payload["symbols_failed"] == []
    assert "verification_status" not in payload


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


def test_execute_with_fake_writer_collects_statuses_and_verification(monkeypatch) -> None:
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_APPROVAL", "YES_APPROVED_MULTI_SYMBOL_WRITE")
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_DATABASE_URL", "postgresql://user:pass@localhost/test")

    calls: list[dict[str, object]] = []

    def fake_writer(payload: dict[str, object]) -> dict[str, object]:
        calls.append(payload)
        symbol = payload["universe"]
        status_map = {
            "QQQ": "WRITE_ACCEPTED",
            "IWM": "IDEMPOTENT_NOOP",
            "DIA": "CONFLICT",
        }
        if symbol == "DIA":
            return {
                "write_status": status_map[symbol],
                "conflict_status": "GRAIN_CONFLICT",
                "dry_run": False,
                "would_write": False,
            }
        return {
            "write_status": status_map[symbol],
            "conflict_status": "NONE",
            "dry_run": False,
            "would_write": symbol == "QQQ",
        }

    verification_calls: list[dict[str, object]] = []

    def fake_verifier(writer_result: dict[str, object], payload: dict[str, object]) -> dict[str, object]:
        verification_calls.append({"writer_result": writer_result, "payload": payload})
        return {
            "verification_status": "VERIFIED",
            "verified_symbol": payload["universe"],
            "verified_idempotency_key_prefix": payload["idempotency_key"][:12],
        }

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(
            ["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15", "--execute"],
            writer_fn=fake_writer,
            verifier_fn=fake_verifier,
        )

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["execute_requested"] is True
    assert payload["db_write_allowed"] is True
    assert payload["db_write_attempted"] is True
    assert payload["production_write_attempted"] is True
    assert payload["production_write_blocked"] is False
    assert payload["symbols_written"] == ["QQQ"]
    assert payload["symbols_noop"] == ["IWM"]
    assert payload["symbols_conflict"] == ["DIA"]
    assert payload["symbols_failed"] == []
    assert payload["per_symbol_write_status"]["QQQ"]["write_status"] == "WRITTEN"
    assert payload["per_symbol_write_status"]["IWM"]["write_status"] == "IDEMPOTENT_NOOP"
    assert payload["per_symbol_write_status"]["DIA"]["write_status"] == "CONFLICT"
    assert payload["verification_status"] == "VERIFIED"
    assert payload["verification_details"]["verified_symbol"] == "IWM"
    assert payload["per_symbol_status"]["QQQ"]["certification_status"] == "PRODUCTION_CANDIDATE"
    assert payload["idempotency_key_prefix"]["QQQ"]
    assert len(payload["idempotency_key_prefix"]["QQQ"]) <= 12
    assert len(calls) == 3
    assert len(verification_calls) == 2


def test_execute_with_fake_writer_failed_symbol_does_not_hide_other_results(monkeypatch) -> None:
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_APPROVAL", "YES_APPROVED_MULTI_SYMBOL_WRITE")
    monkeypatch.setenv("AMM_PRODUCTION_PILOT_DATABASE_URL", "postgresql://user:pass@localhost/test")

    def fake_writer(payload: dict[str, object]) -> dict[str, object]:
        if payload["universe"] == "IWM":
            return {"write_status": "WRITE_FAILED", "error_message": "boom", "conflict_status": "SESSION_FAILURE"}
        return {"write_status": "WRITE_ACCEPTED", "conflict_status": "NONE", "dry_run": False, "would_write": True}

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(
            ["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15", "--execute"],
            writer_fn=fake_writer,
        )

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert "QQQ" in payload["symbols_written"]
    assert "DIA" in payload["symbols_written"]
    assert "IWM" in payload["symbols_failed"]
    assert payload["per_symbol_write_status"]["IWM"]["write_status"] == "FAILED"
    assert payload["per_symbol_write_status"]["QQQ"]["write_status"] == "WRITTEN"


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


def test_source_scan_confirms_no_vendor_live_api_or_scheduler_or_db_adapter_imports() -> None:
    path = Path("scripts/run_market_feature_bundle_multi_symbol_production_seed.py")
    source = path.read_text(encoding="utf-8").lower()
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
        "app.writers.market_feature_bundle_db_adapter",
    ]:
        assert forbidden not in import_names
    assert "requests" not in source
    assert "httpx" not in source


def test_scaffold_doc_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_production_seed_command.md")
    text = path.read_text(encoding="utf-8").lower()
    assert path.exists()
    for needle in [
        "dedicated multi-symbol production seed command scaffold",
        "default dry-run/no-write mode",
        "guarded --execute branch exists for the symbol-agnostic writer contract",
        "production write requires explicit second approval",
        "production write currently blocked unless implementation is explicitly approved",
        "tests use injected fake writer only",
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
        "symbols_written",
        "symbols_noop",
        "symbols_conflict",
        "symbols_failed",
        "per_symbol_write_status",
        "verification_status",
        "production execution still requires user-run command and verification",
    ]:
        assert needle in text
