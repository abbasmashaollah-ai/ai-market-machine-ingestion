from __future__ import annotations

import gzip
import json
from pathlib import Path

from app.vendor_flat_files.options.options_day_aggs_handoff_builder import (
    APPROVAL_PHRASE,
    DEFAULT_SAMPLE_LIMIT,
    MAX_SAMPLE_LIMIT,
    build_options_day_aggs_handoff_sample,
)


def _write_gzip_csv(path: Path, *, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def _sample_path(tmp_path: Path) -> Path:
    return tmp_path / "outputs" / "handoff" / "options_day_aggs" / "options_day_aggs_2025-11-05_sample.jsonl"


def test_default_limit_and_cap() -> None:
    assert DEFAULT_SAMPLE_LIMIT == 100
    assert MAX_SAMPLE_LIMIT == 1000


def test_no_approval_phrase_does_not_write_output(tmp_path) -> None:
    input_path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[["O:SPY251107C00670000", "10", "1.5", "1.6", "1.7", "1.4", "1762318800000000000", "2"]],
    )
    output_path = _sample_path(tmp_path)
    payload = build_options_day_aggs_handoff_sample(input_path=input_path, output_path=output_path)
    assert payload["approval_required"] is True
    assert payload["approval_phrase_matched"] is False
    assert payload["records_written"] == 0
    assert payload["handoff_export_attempted"] is False
    assert output_path.exists() is False


def test_wrong_approval_phrase_does_not_write_output(tmp_path) -> None:
    input_path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[["O:SPY251107C00670000", "10", "1.5", "1.6", "1.7", "1.4", "1762318800000000000", "2"]],
    )
    output_path = _sample_path(tmp_path)
    payload = build_options_day_aggs_handoff_sample(input_path=input_path, output_path=output_path, approval_phrase="WRONG")
    assert payload["approval_phrase_matched"] is False
    assert payload["records_written"] == 0
    assert output_path.exists() is False


def test_approved_sample_write_creates_jsonl_and_hashes(tmp_path) -> None:
    input_path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[
            ["O:SPY251107C00670000", "10", "1.5", "1.6", "1.7", "1.4", "1762318800000000000", "2"],
            ["BADTICKER", "3", "1.0", "1.1", "1.2", "0.9", "1762318800000000000", "1"],
        ],
    )
    output_path = _sample_path(tmp_path)
    payload = build_options_day_aggs_handoff_sample(
        input_path=input_path,
        output_path=output_path,
        approval_phrase=APPROVAL_PHRASE,
        requested_sample_limit=1,
    )
    assert payload["approval_phrase_matched"] is True
    assert payload["records_written"] == 1
    assert payload["output_file_exists"] is True
    assert payload["output_file_size_bytes"] > 0
    assert payload["output_sha256"]
    assert payload["warning_count"] >= 0
    assert output_path.exists() is True
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["contract_symbol"] == "O:SPY251107C00670000"
    assert record["strike_price"] == "670"
    assert record["warnings"] == []


def test_approved_sample_serializes_warnings_safely_and_caps_limit(tmp_path) -> None:
    input_path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        input_path,
        header=["ticker", "volume", "open", "close", "high", "low", "window_start", "transactions"],
        rows=[
            ["BADTICKER", "3", "1.0", "1.1", "1.2", "0.9", "1762318800000000000", "1"],
            ["O:SPY251107C00670000", "4", "1.5", "1.6", "1.4", "1.7", "1762318800000000000", "2"],
        ],
    )
    output_path = _sample_path(tmp_path)
    payload = build_options_day_aggs_handoff_sample(
        input_path=input_path,
        output_path=output_path,
        approval_phrase=APPROVAL_PHRASE,
        requested_sample_limit=5000,
    )
    assert payload["effective_sample_limit"] == MAX_SAMPLE_LIMIT
    assert payload["records_written"] == 2
    assert payload["warning_count"] >= 1
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert first["warnings"]
    assert second["warnings"]
    assert "endpoint" not in json.dumps(payload).lower()
    assert "bucket" not in json.dumps(payload).lower()
    assert "prefix" not in json.dumps(payload).lower()

