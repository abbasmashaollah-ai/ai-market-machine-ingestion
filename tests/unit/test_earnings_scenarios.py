from __future__ import annotations

from app.features.earnings.earnings_builder import build_earnings_observation
from tests.fixtures.earnings_data import build_earnings_fixture_scenario


def test_scenarios_produce_different_labels() -> None:
    upcoming = build_earnings_observation("AAPL", build_earnings_fixture_scenario("upcoming_earnings")["AAPL"], "2026-07-20")
    positive = build_earnings_observation("AAPL", build_earnings_fixture_scenario("positive_reaction")["AAPL"], "2026-08-01")
    negative = build_earnings_observation("TSLA", build_earnings_fixture_scenario("negative_reaction")["TSLA"], "2026-07-30")
    assert upcoming["earnings_regime_label"] == "UPCOMING_EARNINGS_RISK"
    assert positive["earnings_regime_label"] == "POSITIVE_EARNINGS_REACTION"
    assert negative["earnings_regime_label"] == "NEGATIVE_EARNINGS_REACTION"
