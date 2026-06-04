from __future__ import annotations

from app.features.earnings.earnings_job import run_earnings_dry_run
from tests.fixtures.earnings_data import build_earnings_fixture_scenario


def test_dry_run_produces_reports() -> None:
    result = run_earnings_dry_run(build_earnings_fixture_scenario("mixed_earnings"), "2026-07-20")
    assert result.accepted_count == 6
    assert result.rejected_count == 0
    assert len(result.reports) == 6
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True

