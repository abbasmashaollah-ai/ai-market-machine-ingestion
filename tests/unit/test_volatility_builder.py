import json
from copy import deepcopy
from datetime import datetime, timezone

from app.features.volatility.volatility_builder import build_volatility_observation
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_build_observation_fields() -> None:
    histories = build_volatility_series_scenario("elevated_volatility")
    observation = build_volatility_observation(
        histories,
        "2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )
    assert observation["series"] == ["RVX", "VIX", "VVIX", "VXN"]
    assert observation["vix_level"] is not None
    assert observation["vix_close"] == observation["vix_level"]
    assert observation["vvix_close"] == observation["vvix_level"]
    assert observation["vxn_close"] == observation["vxn_level"]
    assert observation["rvx_close"] == observation["rvx_level"]
    assert observation["volatility_stress_score"] == observation["composite_volatility_stress_score"]
    assert observation["descriptive_volatility_state"] == observation["volatility_regime_label"]
    assert observation["volatility_regime_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["source_attribution"] == "fixture_volatility"
    assert observation["dataset_version"] == "volatility_dry_run_v1"
    assert observation["created_at"] == "2026-01-15T00:00:00Z[created_at]"
    assert observation["updated_at"] == "2026-01-15T00:00:00Z[updated_at]"
    json.dumps(observation)


def test_build_observation_preserves_custom_metadata() -> None:
    histories = build_volatility_series_scenario("mixed_volatility")
    metadata = {
        "quality_status": "VALID",
        "certification_status": "CERTIFIED",
        "freshness_status": "FRESH",
        "source_attribution": "unit-test",
        "dataset_version": "custom_version",
        "created_at": "2026-01-15T12:34:56Z",
        "updated_at": "2026-01-15T12:35:56Z",
        "lineage": {"source": "test"},
        "evidence": {"note": "custom"},
    }
    metadata_snapshot = deepcopy(metadata)
    observation = build_volatility_observation(
        histories,
        "2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
        source="fixture_volatility",
        metadata=metadata,
    )

    assert observation["quality_status"] == "VALID"
    assert observation["certification_status"] == "CERTIFIED"
    assert observation["freshness_status"] == "FRESH"
    assert observation["source_attribution"] == "unit-test"
    assert observation["dataset_version"] == "custom_version"
    assert observation["created_at"] == "2026-01-15T12:34:56Z"
    assert observation["updated_at"] == "2026-01-15T12:35:56Z"
    assert observation["lineage"] == {"source": "test"}
    assert observation["evidence"] == {"note": "custom"}
    assert metadata == metadata_snapshot
    json.dumps(observation)


def test_build_observation_keeps_default_alias_behavior_without_metadata() -> None:
    observation = build_volatility_observation(
        build_volatility_series_scenario("low_volatility"),
        "2026-01-15",
    )
    assert observation["source_attribution"] == "fixture_volatility"
    assert observation["descriptive_volatility_state"] == observation["volatility_regime_label"]
    assert observation["dataset_version"] == "volatility_dry_run_v1"
