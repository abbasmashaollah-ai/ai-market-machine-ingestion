import json
from datetime import datetime, timezone

from app.features.options.options_builder import build_options_observation
from tests.fixtures.options_data import build_options_metrics_scenario


def test_observation_fields() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert observation["symbol"] == "NVDA"
    assert observation["underlying_symbol"] == "NVDA"
    assert observation["observation_date"] == "2026-01-15"
    assert observation["options_regime_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["no_db_writes"] is True
    json.dumps(observation)


def test_observation_preserves_optional_fields() -> None:
    metrics = dict(build_options_metrics_scenario("high_volatility")["NVDA"])
    metrics["underlying_symbol"] = "QQQ"
    metrics["expiration_date"] = "2026-06-19"
    metrics["total_volume"] = 123456
    metrics["total_open_interest"] = 789012
    observation = build_options_observation("NVDA", metrics, "2026-01-15")
    assert observation["underlying_symbol"] == "QQQ"
    assert observation["expiration_date"] == "2026-06-19"
    assert observation["total_volume"] == 123456
    assert observation["total_open_interest"] == 789012
