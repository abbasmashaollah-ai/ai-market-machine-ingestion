import json

from app.features.volatility.volatility_builder import build_volatility_observation
from app.features.volatility.volatility_report import build_volatility_report
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_report_is_json_friendly_and_contains_state() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("mixed_volatility"), "2026-01-15")
    report = build_volatility_report(observation)
    assert report["volatility_regime_label"]
    assert report["no_db_writes"] is True
    json.dumps(report)
