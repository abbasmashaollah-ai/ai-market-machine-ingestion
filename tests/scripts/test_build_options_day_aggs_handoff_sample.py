from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_help_mentions_approval_phrase() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_options_day_aggs_handoff_sample.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "APPROVE OPTIONS DAY AGGS SAMPLE HANDOFF BUILD" in result.stdout


def test_script_no_approval_is_safe(tmp_path) -> None:
    input_path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text("placeholder", encoding="utf-8")
    output_path = tmp_path / "outputs" / "handoff" / "options_day_aggs" / "options_day_aggs_2025-11-05_sample.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_options_day_aggs_handoff_sample.py",
            "--input-path",
            str(input_path),
            "--output-path",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["approval_phrase_matched"] is False
    assert payload["handoff_export_attempted"] is False
    assert output_path.exists() is False


def test_script_approved_writes_sample(tmp_path) -> None:
    import gzip

    input_path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    with gzip.open(input_path, "wt", encoding="utf-8", newline="") as handle:
        handle.write("ticker,volume,open,close,high,low,window_start,transactions\n")
        handle.write("O:SPY251107C00670000,10,1.5,1.6,1.7,1.4,1762318800000000000,2\n")
    output_path = tmp_path / "outputs" / "handoff" / "options_day_aggs" / "options_day_aggs_2025-11-05_sample.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_options_day_aggs_handoff_sample.py",
            "--input-path",
            str(input_path),
            "--output-path",
            str(output_path),
            "--approval-phrase",
            "APPROVE OPTIONS DAY AGGS SAMPLE HANDOFF BUILD",
            "--sample-limit",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["approval_phrase_matched"] is True
    assert payload["records_written"] == 1
    assert payload["output_file_exists"] is True
    assert output_path.exists() is True

