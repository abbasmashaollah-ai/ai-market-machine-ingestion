import json

from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from app.features.fundamentals.fundamentals_report import build_fundamental_report
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_report_contains_expected_fields() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    report = build_fundamental_report(observation, writer_result=type("R", (), {"accepted_count": 1, "rejected_count": 0})())
    assert report["symbol"] == "AAPL"
    assert report["fundamental_quality_label"]
    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["safety_flags"]["no_db_writes"] is True
    json.dumps(report)
