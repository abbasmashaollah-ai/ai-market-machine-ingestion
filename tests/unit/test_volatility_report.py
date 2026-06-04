import json

from app.features.volatility.volatility_builder import build_volatility_observation
from app.features.volatility.volatility_report import build_volatility_report
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_report_is_json_friendly_and_contains_state() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("mixed_volatility"), "2026-01-15")
    report = build_volatility_report(observation)
    assert report["volatility_regime_label"]
    assert report["vix_close"] == report["vix_level"]
    assert report["vvix_close"] == report["vvix_level"]
    assert report["vxn_close"] == report["vxn_level"]
    assert report["rvx_close"] == report["rvx_level"]
    assert report["volatility_stress_score"] == report["composite_volatility_stress_score"]
    assert report["descriptive_volatility_state"] == report["volatility_regime_label"]
    assert report["dataset_version"] == "volatility_dry_run_v1"
    assert report["created_at"] == "2026-01-15T00:00:00Z[created_at]"
    assert report["updated_at"] == "2026-01-15T00:00:00Z[updated_at]"
    assert report["no_db_writes"] is True
    json.dumps(report)
