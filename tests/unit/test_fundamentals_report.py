import json

from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from app.features.fundamentals.fundamentals_report import build_fundamental_report
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_report_contains_expected_fields() -> None:
    financials = dict(build_fundamentals_financials_scenario("strong_quality")["AAPL"])
    financials["source_attribution"] = "custom_source"
    financials["dataset_version"] = "custom_dataset_v2"
    financials["created_at"] = "2026-01-14T22:00:00Z"
    financials["updated_at"] = "2026-01-15T10:00:00Z"
    observation = build_fundamental_observation("AAPL", financials, "2026-01-15")
    report = build_fundamental_report(observation, writer_result=type("R", (), {"accepted_count": 1, "rejected_count": 0})())
    assert report["symbol"] == "AAPL"
    assert report["source_attribution"] == "custom_source"
    assert report["dataset_version"] == "custom_dataset_v2"
    assert report["created_at"] == "2026-01-14T22:00:00Z"
    assert report["updated_at"] == "2026-01-15T10:00:00Z"
    assert report["fundamental_quality_label"]
    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["safety_flags"]["no_db_writes"] is True
    json.dumps(report)
