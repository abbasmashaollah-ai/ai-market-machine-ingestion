from __future__ import annotations

import io
import json
import ast
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys

from scripts.run_market_feature_bundle_multi_symbol_dry_run import main


FIXTURE_DIR = Path("tests/fixtures/market_feature_bundle")


def test_default_run_validates_qqq_iwm_dia_fixtures() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--observation-date", "2026-01-15"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["dry_run"] is True
    assert payload["symbols_requested"] == ["QQQ", "IWM", "DIA"]
    assert payload["symbols_succeeded"] == ["QQQ", "IWM", "DIA"]
    assert payload["symbols_failed"] == []
    assert payload["validation_status"] == "PASS"
    assert payload["coverage_status"] == "COMPLETE"
    assert payload["quality_status"] == "PASS"
    assert payload["certification_status"] == "CERTIFIED"
    assert payload["db_write_attempted"] is False
    assert payload["production_write_attempted"] is False
    assert payload["vendor_call_attempted"] is False
    assert payload["live_api_call_attempted"] is False
    assert payload["scheduler_activation_attempted"] is False
    assert payload["per_symbol_status"]["QQQ"]["status"] == "PASS"
    assert payload["per_symbol_status"]["IWM"]["status"] == "PASS"
    assert payload["per_symbol_status"]["DIA"]["status"] == "PASS"


def test_custom_symbols_subset_works() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM", "--observation-date", "2026-01-15"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["symbols_requested"] == ["QQQ", "IWM"]
    assert payload["symbols_succeeded"] == ["QQQ", "IWM"]
    assert payload["symbols_failed"] == []
    assert set(payload["per_symbol_status"]) == {"QQQ", "IWM"}


def test_missing_fixture_returns_insufficient_evidence(tmp_path: Path) -> None:
    temp_fixture_dir = tmp_path / "tests" / "fixtures" / "market_feature_bundle"
    temp_fixture_dir.mkdir(parents=True)
    for name in ["iwm", "dia"]:
        (temp_fixture_dir / f"{name}_fixture_dry_run.json").write_text((FIXTURE_DIR / f"{name}_fixture_dry_run.json").read_text(encoding="utf-8"), encoding="utf-8")

    from scripts import run_market_feature_bundle_multi_symbol_dry_run as mod

    original_fixture_dir = mod.FIXTURE_DIR
    try:
        mod.FIXTURE_DIR = temp_fixture_dir
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = mod.main(["--observation-date", "2026-01-15"])
    finally:
        mod.FIXTURE_DIR = original_fixture_dir

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["symbols_requested"] == ["QQQ", "IWM", "DIA"]
    assert payload["symbols_failed"] == ["QQQ"]
    assert payload["per_symbol_status"]["QQQ"]["status"] == "INSUFFICIENT_EVIDENCE"
    assert payload["per_symbol_status"]["QQQ"]["reason"] == "fixture missing"


def test_invalid_fixture_returns_failed_symbol_without_crash(tmp_path: Path) -> None:
    temp_fixture_dir = tmp_path / "tests" / "fixtures" / "market_feature_bundle"
    temp_fixture_dir.mkdir(parents=True)
    for name in ["qqq", "iwm", "dia"]:
        (temp_fixture_dir / f"{name}_fixture_dry_run.json").write_text((FIXTURE_DIR / f"{name}_fixture_dry_run.json").read_text(encoding="utf-8"), encoding="utf-8")

    bad_path = temp_fixture_dir / "iwm_fixture_dry_run.json"
    bad_payload = json.loads(bad_path.read_text(encoding="utf-8"))
    bad_payload["validation_status"] = "FAIL"
    bad_path.write_text(json.dumps(bad_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    from scripts import run_market_feature_bundle_multi_symbol_dry_run as mod

    original_fixture_dir = mod.FIXTURE_DIR
    try:
        mod.FIXTURE_DIR = temp_fixture_dir
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = mod.main(["--observation-date", "2026-01-15"])
    finally:
        mod.FIXTURE_DIR = original_fixture_dir

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["symbols_requested"] == ["QQQ", "IWM", "DIA"]
    assert payload["per_symbol_status"]["IWM"]["status"] == "FAILED"
    assert payload["per_symbol_status"]["IWM"]["reason"] == "fixture validation failed"
    assert "invalid validation_status" in payload["per_symbol_status"]["IWM"]["errors"]


def test_output_file_writes_local_dry_run_json_summary(tmp_path: Path) -> None:
    output_file = tmp_path / "outputs" / "dry_runs" / "market_feature_bundle_multi_symbol.json"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--observation-date", "2026-01-15", "--output-file", str(output_file)])

    assert exit_code == 0
    stdout_payload = json.loads(buffer.getvalue())
    file_payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert file_payload["idempotency_key_prefix"]["QQQ"]
    assert file_payload["db_write_attempted"] is False
    assert file_payload["production_write_attempted"] is False
    assert file_payload["vendor_call_attempted"] is False


def test_source_scan_confirms_no_writer_db_vendor_live_or_scheduler_imports() -> None:
    source = Path("scripts/run_market_feature_bundle_multi_symbol_dry_run.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_names.add(node.module.lower())

    for forbidden in [
        "market_feature_bundle_db_adapter",
        "market_feature_bundle_writer",
        "requests",
        "httpx",
        "vendor",
        "provider",
        "scheduler",
        "engine",
        "session",
        "database",
    ]:
        assert forbidden not in import_names


def test_no_secrets_tokens_or_raw_provider_credentials_in_output() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15"])

    assert exit_code == 0
    text = buffer.getvalue().lower()
    for forbidden in ["secret", "token", "credential", "api_key", "apikey", "raw_provider"]:
        assert forbidden not in text


def test_cli_runs_as_subprocess_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_market_feature_bundle_multi_symbol_dry_run.py", "--symbols", "QQQ,IWM,DIA", "--observation-date", "2026-01-15"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["symbols_requested"] == ["QQQ", "IWM", "DIA"]
    assert payload["db_write_attempted"] is False
    assert payload["production_write_attempted"] is False
