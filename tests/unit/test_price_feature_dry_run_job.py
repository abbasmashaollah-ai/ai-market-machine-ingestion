import json
from datetime import datetime, timezone

from app.features.prices.price_feature_job import run_price_feature_dry_run
from tests.fixtures.price_ohlcv import build_price_ohlcv_fixtures


def test_dry_run_creates_expected_observations_and_reports() -> None:
    fixtures = build_price_ohlcv_fixtures()

    result = run_price_feature_dry_run(
        fixtures,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )

    symbols = [row["symbol"] for row in result.observation_rows]

    assert symbols == ["SPY", "AAPL", "MSFT"]
    assert result.accepted_count == 3
    assert result.rejected_count == 0
    assert len(result.reports) == 3
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True


def test_dry_run_reports_are_json_friendly() -> None:
    fixtures = build_price_ohlcv_fixtures()

    result = run_price_feature_dry_run(fixtures, observation_date="2026-01-15")

    json.dumps([dict(report) for report in result.reports])