import json
from datetime import datetime, timezone

from app.features.breadth.breadth_job import run_breadth_dry_run
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def test_dry_run_produces_report_and_safety_flags() -> None:
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}

    result = run_breadth_dry_run(
        fixtures,
        volume_histories,
        universe="SP500",
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert result.reports
    json.dumps([dict(report) for report in result.reports])
