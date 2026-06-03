import json
from datetime import datetime, timezone

from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_observation_fields() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert observation["symbol"] == "AAPL"
    assert observation["observation_date"] == "2026-01-15"
    assert observation["fundamental_quality_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["no_db_writes"] is True
    json.dumps(observation)
