from app.features.cross_asset.cross_asset_builder import build_cross_asset_observation
from app.features.cross_asset.cross_asset_validator import validate_cross_asset_observation, validate_cross_asset_observations
from tests.fixtures.cross_asset_ohlcv import build_cross_asset_ohlcv_fixtures


def test_valid_observation_passes() -> None:
    observation = build_cross_asset_observation(build_cross_asset_ohlcv_fixtures(), "2026-01-15")
    assert validate_cross_asset_observation(observation).is_valid is True


def test_invalid_rows_fail_and_duplicates_fail() -> None:
    observation = dict(build_cross_asset_observation(build_cross_asset_ohlcv_fixtures(), "2026-01-15"))
    observation["symbols"] = []
    observation["risk_on_alignment_flag"] = "yes"
    result = validate_cross_asset_observation(observation)
    assert result.is_valid is False
    duplicate_results = validate_cross_asset_observations([observation, observation])
    assert duplicate_results[1].is_valid is False