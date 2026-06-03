import json
from datetime import datetime, timezone

from app.features.volatility.volatility_job import run_volatility_dry_run
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    histories = build_volatility_series_scenario("high_volatility")
    result = run_volatility_dry_run(histories, "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert result.accepted_count == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    json.dumps([dict(report) for report in result.reports])
