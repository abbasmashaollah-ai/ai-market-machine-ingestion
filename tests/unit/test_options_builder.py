import json
from datetime import datetime, timezone

from app.features.options.options_builder import build_options_observation
from tests.fixtures.options_data import build_options_metrics_scenario


def test_observation_fields() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert observation["symbol"] == "NVDA"
    assert observation["underlying_symbol"] == "NVDA"
    assert observation["source_attribution"] == "fixture_options"
    assert observation["dataset_version"] == "options_dry_run_v1"
    assert observation["created_at"] == "2026-01-15T00:00:00Z[created_at]"
    assert observation["updated_at"] == "2026-01-15T00:00:00Z[updated_at]"
    assert observation["observation_date"] == "2026-01-15"
    assert observation["options_regime_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["no_db_writes"] is True
    json.dumps(observation)


def test_observation_preserves_optional_fields() -> None:
    metrics = dict(build_options_metrics_scenario("high_volatility")["NVDA"])
    metrics["source_attribution"] = "custom_source"
    metrics["dataset_version"] = "custom_dataset_v2"
    metrics["created_at"] = "2026-01-14T22:00:00Z"
    metrics["updated_at"] = "2026-01-15T10:00:00Z"
    metrics["underlying_symbol"] = "QQQ"
    metrics["expiration_date"] = "2026-06-19"
    metrics["total_volume"] = 123456
    metrics["total_open_interest"] = 789012
    observation = build_options_observation("NVDA", metrics, "2026-01-15")
    assert observation["source_attribution"] == "custom_source"
    assert observation["dataset_version"] == "custom_dataset_v2"
    assert observation["created_at"] == "2026-01-14T22:00:00Z"
    assert observation["updated_at"] == "2026-01-15T10:00:00Z"
    assert observation["underlying_symbol"] == "QQQ"
    assert observation["expiration_date"] == "2026-06-19"
    assert observation["total_volume"] == 123456
    assert observation["total_open_interest"] == 789012
