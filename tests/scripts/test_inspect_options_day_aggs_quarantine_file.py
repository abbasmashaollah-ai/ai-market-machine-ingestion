from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import scripts.inspect_options_day_aggs_quarantine_file as cli


def _write_gzip_csv(path: Path, *, header: list[str], rows: list[list[str]]) -> None:
    import gzip

    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def _run_cli(argv: list[str]) -> dict[str, object]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(argv)
    assert exit_code == 0
    return json.loads(buffer.getvalue())


def test_default_path_missing_file_is_safe() -> None:
    payload = _run_cli(["--input-path", "outputs/quarantine/options_flat_files/does_not_exist.csv.gz"])
    assert payload["input_file_exists"] is False
    assert payload["row_count"] == 0
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False


def test_cli_reads_local_file_and_reports_safe_samples(tmp_path) -> None:
    path = tmp_path / "massive_options_day_aggs_2025-11-05.csv.gz"
    _write_gzip_csv(
        path,
        header=["contract_symbol", "symbol", "date", "strike", "type"],
        rows=[
            ["OPT1", "SPY", "2025-11-05", "600", "call"],
            ["OPT2", "QQQ", "2025-11-05", "500", "put"],
        ],
    )
    payload = _run_cli(["--input-path", str(path), "--sample-rows", "1"])
    assert payload["input_file_exists"] is True
    assert payload["row_count"] == 2
    assert payload["safe_sample_rows_count"] == 1
    assert payload["safe_sample_rows"][0]["symbol"] == "SPY"
    assert payload["vendor_call_attempted"] is False
    assert payload["download_attempted"] is False
    text = json.dumps(payload).lower()
    for forbidden in ["endpoint.invalid", "bucket", "prefix", "us_options_opra/day_aggs_v1", "etag", "secret"]:
        assert forbidden not in text


def test_help_mentions_input_path_and_sample_rows() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/inspect_options_day_aggs_quarantine_file.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--input-path" in result.stdout
    assert "--sample-rows" in result.stdout
