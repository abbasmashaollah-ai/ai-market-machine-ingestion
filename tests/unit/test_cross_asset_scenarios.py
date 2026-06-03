from app.features.cross_asset.cross_asset_builder import build_cross_asset_observation
from app.features.cross_asset.cross_asset_report import build_cross_asset_report
from tests.fixtures.cross_asset_ohlcv import build_cross_asset_fixture_histories_scenario


def _report_for_scenario(scenario: str) -> dict[str, object]:
    close_histories, _ = build_cross_asset_fixture_histories_scenario(scenario)
    observation = build_cross_asset_observation(close_histories, "2026-01-15")
    return build_cross_asset_report(observation)


def test_scenario_labels_differ() -> None:
    risk_on = _report_for_scenario("risk_on")
    risk_off = _report_for_scenario("risk_off")
    mixed = _report_for_scenario("mixed")
    divergence = _report_for_scenario("equity_credit_divergence")

    assert risk_on["descriptive_intermarket_state"] != risk_off["descriptive_intermarket_state"]
    assert mixed["descriptive_intermarket_state"] in {
        "MIXED_INTERMARKET",
        "INSUFFICIENT_DATA",
        "RISK_ON_CONFIRMATION",
        "RISK_OFF_PRESSURE",
        "EQUITY_CREDIT_DIVERGENCE",
        "RATES_PRESSURE",
        "DOLLAR_PRESSURE",
    }
    assert divergence["descriptive_intermarket_state"] in {"EQUITY_CREDIT_DIVERGENCE", "MIXED_INTERMARKET"}