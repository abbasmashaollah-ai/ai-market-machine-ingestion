from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts import dry_run_breadth_observations_handoff as script


def test_dry_run_handoff_script_writes_jsonl_and_reports_evidence(tmp_path: Path) -> None:
    output_file = tmp_path / "breadth.jsonl"
    quarantine_file = tmp_path / "quarantine.jsonl"

    with patch("builtins.print") as print_mock:
        exit_code = script.main(
            [
                "--output-file",
                str(output_file),
                "--quarantine-file",
                str(quarantine_file),
                "--summary-only",
            ]
        )

    assert exit_code == 0
    assert output_file.exists()
    records = [json.loads(line) for line in output_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 1
    record = records[0]
    assert record["universe_key"] == "SP500"
    assert record["source_vendor"] == "fixture_vendor"
    assert record["source_dataset"] == "breadth_observations"
    assert record["source_sha256"] == "fixture-source-sha256"
    assert "advance_decline_line" not in record
    assert "breadth_score" not in record
    assert "participation_score" not in record
    assert "participation_label" not in record
    assert record["metadata"]["trace"]["advance_decline_line"] is not None

    printed = " ".join(str(arg) for call in print_mock.mock_calls for arg in call.args)
    assert '"input_row_count": 1' in printed
    assert '"accepted_row_count": 1' in printed
    assert '"rejected_quarantined_row_count": 0' in printed
    assert '"idempotency_key_coverage": true' in printed
    assert '"no_production_change": true' in printed
    assert '"schema_version": "breadth_observations_jsonl_v1"' in printed
    assert '"generated_artifact_path":' in printed


def test_dry_run_handoff_script_rejects_invalid_local_rows_via_builder(tmp_path: Path) -> None:
    from app.features.breadth.breadth_jsonl_handoff_builder import write_breadth_observations_handoff_jsonl
    from app.features.breadth.breadth_observation_builder import build_breadth_observation
    from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures

    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}
    observation = build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")
    observation["source"] = "fixture_vendor"
    observation["source_dataset"] = "breadth_observations"
    observation["source_sha256"] = "fixture-source-sha256"
    observation["metadata"] = {"trace": {"advance_decline_line": 1}}

    result = write_breadth_observations_handoff_jsonl(
        [observation, dict(observation, advancing_count=-1)],
        tmp_path / "breadth.jsonl",
        source_vendor="fixture_vendor",
        source_dataset="breadth_observations",
        source_sha256="fixture-source-sha256",
        quarantine_path=tmp_path / "quarantine.jsonl",
        generated_at="2026-01-15T16:00:00Z",
    )
    assert result.records_received == 2
    assert result.records_written == 1
    assert result.records_rejected == 1
    assert result.quarantine_path is not None
    assert Path(result.quarantine_path).exists()
