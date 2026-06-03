import json
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
    assert observation["volatility_regime_label"]
    assert observation["quality_status"] == "PENDING"
    json.dumps(observation)
