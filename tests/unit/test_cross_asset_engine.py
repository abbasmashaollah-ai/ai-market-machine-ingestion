from app.features.cross_asset.cross_asset_engine import (
    calculate_asset_returns,
    calculate_commodity_pressure_score,
    calculate_credit_risk_score,
    calculate_dollar_pressure_score,
    calculate_equity_leadership_score,
    calculate_intermarket_alignment_score,
    calculate_rates_pressure_score,
    calculate_volatility_pressure_score,
    determine_descriptive_intermarket_state,
)


def test_returns_and_scores() -> None:
    histories = {
        "SPY": [{"close": v} for v in [100, 101, 102, 103, 104, 105]],
        "QQQ": [{"close": v} for v in [100, 102, 104, 106, 108, 110]],
        "IWM": [{"close": v} for v in [100, 99, 98, 97, 96, 95]],
        "HYG": [{"close": v} for v in [100, 101, 102, 103, 104, 105]],
        "TLT": [{"close": v} for v in [100, 99, 98, 97, 96, 95]],
        "GLD": [{"close": v} for v in [100, 101, 102, 103, 104, 105]],
        "USO": [{"close": v} for v in [100, 99, 98, 97, 96, 95]],
        "DXY": [{"close": v} for v in [100, 101, 102, 103, 104, 105]],
        "VIX": [{"close": v} for v in [100, 99, 98, 97, 96, 95]],
    }
    returns = calculate_asset_returns(histories)
    assert returns["SPY"][5] is not None
    components = {
        "equity_leadership_score": calculate_equity_leadership_score(returns),
        "credit_risk_score": calculate_credit_risk_score(returns),
        "rates_pressure_score": calculate_rates_pressure_score(returns),
        "dollar_pressure_score": calculate_dollar_pressure_score(returns),
        "commodity_pressure_score": calculate_commodity_pressure_score(returns),
        "volatility_pressure_score": calculate_volatility_pressure_score(returns),
    }
    components["intermarket_alignment_score"] = calculate_intermarket_alignment_score(components)
    assert determine_descriptive_intermarket_state(components)