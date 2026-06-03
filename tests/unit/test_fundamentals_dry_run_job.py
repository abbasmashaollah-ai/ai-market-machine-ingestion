import json

from app.features.fundamentals.fundamentals_job import run_fundamentals_dry_run
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_dry_run_produces_reports_and_safety_flags() -> None:
    result = run_fundamentals_dry_run(build_fundamentals_financials_scenario("mixed_quality"), "2026-01-15")
    assert result.accepted_count == 6
    assert result.rejected_count == 0
    assert len(result.reports) == 6
    assert result.reports[0]["safety_flags"]["no_db_writes"] is True
    json.dumps(result.reports[0])
