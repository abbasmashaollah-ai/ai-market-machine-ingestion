import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys

from scripts.run_market_feature_bundle_dry_run import main


def test_cli_prints_bundle_json_and_safety_flags() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--observation-date", "2026-01-15", "--timestamp", "2026-01-15T16:00:00Z"])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["no_db_writes"] is True
    assert payload["no_vendor_calls"] is True
    assert payload["no_live_api_calls"] is True
    assert payload["no_scheduler_activation"] is True
    assert payload["prices"]["reports_by_symbol"]["SPY"]
    assert payload["breadth"]["report"]["participation_label"]
    assert payload["sector_rotation"]["descriptive_rotation_state"]
    assert payload["cross_asset"]["descriptive_intermarket_state"]
    assert payload["liquidity_rates"]["liquidity_regime_label"]
    assert payload["volatility"]["volatility_regime_label"]
    assert payload["event_calendar"]["event_risk_label"]
    assert payload["news_sentiment"]["sentiment_regime_label"]
    assert payload["fundamentals"]["reports_by_symbol"]["AAPL"]["fundamental_quality_label"]


def test_cli_writes_output_file_and_matches_stdout(tmp_path: Path) -> None:
    output_file = tmp_path / "outputs" / "dry_runs" / "bundle.json"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--observation-date", "2026-01-15", "--output-file", str(output_file)])

    assert exit_code == 0
    stdout_payload = json.loads(buffer.getvalue())
    file_payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert output_file.parent.is_dir()
    assert file_payload["no_db_writes"] is True
    assert file_payload["no_vendor_calls"] is True
    assert file_payload["no_live_api_calls"] is True
    assert file_payload["no_scheduler_activation"] is True


def test_cli_uses_defaults_when_arguments_omitted() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["observation_date"] == "2026-01-15"


def test_cli_summary_only_writes_compact_summary(tmp_path: Path) -> None:
    output_file = tmp_path / "outputs" / "dry_runs" / "market_feature_bundle_summary_fixture.json"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(["--observation-date", "2026-01-15", "--summary-only", "--output-file", str(output_file)])

    assert exit_code == 0
    stdout_payload = json.loads(buffer.getvalue())
    file_payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert stdout_payload["price_states_by_symbol"]["SPY"]
    assert stdout_payload["breadth_participation_label"]
    assert stdout_payload["sector_rotation_state"]
    assert stdout_payload["cross_asset_state"]
    assert stdout_payload["liquidity_rates_state"]
    assert stdout_payload["volatility_state"]
    assert stdout_payload["event_calendar_state"]
    assert stdout_payload["news_sentiment_state"]
    assert stdout_payload["fundamental_quality_labels_by_symbol"]["AAPL"]
    assert stdout_payload["safety_flags"]["no_db_writes"] is True
    assert stdout_payload["safety_flags"]["no_vendor_calls"] is True
    assert stdout_payload["safety_flags"]["no_live_api_calls"] is True
    assert stdout_payload["safety_flags"]["no_scheduler_activation"] is True
    assert "prices" not in stdout_payload
    assert "liquidity_rates" not in stdout_payload
    assert "volatility" not in stdout_payload
    assert "event_calendar" not in stdout_payload
    assert "news_sentiment" not in stdout_payload
    assert "fundamental_quality_labels_by_symbol" in stdout_payload


def test_cli_runs_as_subprocess_from_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_market_feature_bundle_dry_run.py", "--observation-date", "2026-06-03", "--summary-only"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["descriptive_market_evidence_state"]
    assert payload["safety_flags"]["no_db_writes"] is True
    assert payload["safety_flags"]["no_vendor_calls"] is True
    assert payload["safety_flags"]["no_live_api_calls"] is True
    assert payload["safety_flags"]["no_scheduler_activation"] is True
