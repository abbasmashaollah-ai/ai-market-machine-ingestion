from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_scenarios_produce_different_labels() -> None:
    strong = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")["fundamental_quality_label"]
    mixed = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("mixed_quality")["AAPL"], "2026-01-15")["fundamental_quality_label"]
    weak = build_fundamental_observation("TSLA", build_fundamentals_financials_scenario("weak_quality")["TSLA"], "2026-01-15")["fundamental_quality_label"]
    distressed = build_fundamental_observation("TSLA", build_fundamentals_financials_scenario("distressed_quality")["TSLA"], "2026-01-15")["fundamental_quality_label"]
    assert strong in {"STRONG_FUNDAMENTALS", "HEALTHY_FUNDAMENTALS"}
    assert mixed in {"MIXED_FUNDAMENTALS", "HEALTHY_FUNDAMENTALS"}
    assert weak in {"WEAK_FUNDAMENTALS", "MIXED_FUNDAMENTALS"}
    assert distressed in {"DISTRESSED_FUNDAMENTALS", "WEAK_FUNDAMENTALS"}
