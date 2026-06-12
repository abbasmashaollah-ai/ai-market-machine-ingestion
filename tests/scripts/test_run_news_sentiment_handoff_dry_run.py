from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_script_writes_fixture_jsonl(tmp_path: Path) -> None:
    output_file = tmp_path / "handoff.jsonl"
    result = subprocess.run(
        [sys.executable, "scripts/run_news_sentiment_handoff_dry_run.py", "--output-file", str(output_file), "--summary-only"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["records_written"] == 3
    assert payload["no_vendor_calls"] is True
    assert payload["no_db_writes"] is True
    assert output_file.exists()

