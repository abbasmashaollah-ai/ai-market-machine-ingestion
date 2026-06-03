import json
from datetime import datetime, timezone

from app.features.cross_asset.cross_asset_job import run_cross_asset_dry_run
from tests.fixtures.cross_asset_ohlcv import build_cross_asset_fixture_histories_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    close_histories, _ = build_cross_asset_fixture_histories_scenario("risk_on")
    result = run_cross_asset_dry_run(close_histories, "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert result.accepted_count == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    json.dumps([dict(report) for report in result.reports])