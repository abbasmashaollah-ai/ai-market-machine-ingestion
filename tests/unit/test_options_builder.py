import json
from datetime import datetime, timezone

from app.features.options.options_builder import build_options_observation
from tests.fixtures.options_data import build_options_metrics_scenario


def test_observation_fields() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert observation["symbol"] == "NVDA"
    assert observation["observation_date"] == "2026-01-15"
    assert observation["options_regime_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["no_db_writes"] is True
    json.dumps(observation)
