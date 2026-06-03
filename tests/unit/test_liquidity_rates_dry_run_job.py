import json
from datetime import datetime, timezone

from app.features.liquidity_rates.liquidity_rates_job import run_liquidity_rates_dry_run
from tests.fixtures.liquidity_rates_series import build_liquidity_rates_series_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    histories = build_liquidity_rates_series_scenario("liquidity_tailwind")
    result = run_liquidity_rates_dry_run(histories, "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert result.accepted_count == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    json.dumps([dict(report) for report in result.reports])