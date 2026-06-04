import json

from app.features.options.options_builder import build_options_observation
from app.features.options.options_report import build_options_report
from tests.fixtures.options_data import build_options_metrics_scenario


def test_report_contains_expected_fields() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    report = build_options_report(observation, writer_result=type("R", (), {"accepted_count": 1, "rejected_count": 0})())
    assert report["symbol"] == "NVDA"
    assert report["options_regime_label"]
    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["safety_flags"]["no_db_writes"] is True
    json.dumps(report)
