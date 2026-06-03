import json

from app.features.cross_asset.cross_asset_builder import build_cross_asset_observation
from tests.fixtures.cross_asset_ohlcv import build_cross_asset_ohlcv_fixtures


def test_observation_has_expected_fields() -> None:
    observation = build_cross_asset_observation(build_cross_asset_ohlcv_fixtures(), "2026-01-15")
    expected_fields = {
        "observation_date",
        "timestamp",
        "symbols",
        "equity_leadership_score",
        "credit_risk_score",
        "rates_pressure_score",
        "dollar_pressure_score",
        "commodity_pressure_score",
        "volatility_pressure_score",
        "intermarket_alignment_score",
        "risk_on_alignment_flag",
        "risk_off_alignment_flag",
        "divergence_flag",
        "descriptive_intermarket_state",
        "source",
        "quality_status",
        "certification_status",
        "freshness_status",
        "lineage",
        "evidence",
    }
    assert set(observation) == expected_fields
    json.dumps(observation)