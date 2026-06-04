import json

from app.features.options.options_builder import build_options_observation
from app.features.options.options_report import build_options_report
from tests.fixtures.options_data import build_options_metrics_scenario


def test_report_contains_expected_fields() -> None:
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
    report = build_options_report(observation, writer_result=type("R", (), {"accepted_count": 1, "rejected_count": 0})())
    assert report["symbol"] == "NVDA"
    assert report["source_attribution"] == "custom_source"
    assert report["dataset_version"] == "custom_dataset_v2"
    assert report["created_at"] == "2026-01-14T22:00:00Z"
    assert report["updated_at"] == "2026-01-15T10:00:00Z"
    assert report["underlying_symbol"] == "QQQ"
    assert report["expiration_date"] == "2026-06-19"
    assert report["total_volume"] == 123456
    assert report["total_open_interest"] == 789012
    assert report["options_regime_label"]
    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["safety_flags"]["no_db_writes"] is True
    json.dumps(report)
