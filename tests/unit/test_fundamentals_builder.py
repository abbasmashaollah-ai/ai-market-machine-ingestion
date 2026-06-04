import json
from datetime import datetime, timezone

from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_observation_fields() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert observation["symbol"] == "AAPL"
    assert observation["observation_date"] == "2026-01-15"
    assert observation["source_attribution"] == "fixture_fundamentals"
    assert observation["dataset_version"] == "fundamentals_dry_run_v1"
    assert observation["created_at"] == "2026-01-15T00:00:00Z"
    assert observation["updated_at"] == "2026-01-15T00:00:00Z"
    assert observation["fundamental_quality_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["no_db_writes"] is True
    json.dumps(observation)


def test_observation_preserves_metadata_fields() -> None:
    financials = dict(build_fundamentals_financials_scenario("strong_quality")["AAPL"])
    financials["source_attribution"] = "custom_source"
    financials["dataset_version"] = "custom_dataset_v2"
    financials["created_at"] = "2026-01-14T22:00:00Z"
    financials["updated_at"] = "2026-01-15T10:00:00Z"
    observation = build_fundamental_observation("AAPL", financials, "2026-01-15")
    assert observation["source_attribution"] == "custom_source"
    assert observation["dataset_version"] == "custom_dataset_v2"
    assert observation["created_at"] == "2026-01-14T22:00:00Z"
    assert observation["updated_at"] == "2026-01-15T10:00:00Z"
