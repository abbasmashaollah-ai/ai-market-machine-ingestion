import io
import json
from contextlib import redirect_stdout
from datetime import datetime, timezone

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


def test_cli_uses_defaults_when_arguments_omitted() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main([])

    assert exit_code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["observation_date"] == "2026-01-15"