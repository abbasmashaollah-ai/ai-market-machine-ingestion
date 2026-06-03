from app.features.liquidity_rates.liquidity_rates_universe import get_liquidity_rates_series, get_required_liquidity_rates_series, is_liquidity_rates_series


def test_universe_helpers() -> None:
    series = get_liquidity_rates_series()
    assert "FED_FUNDS" in series
    assert "SPY" in series
    assert is_liquidity_rates_series("fed_funds") is True
    assert is_liquidity_rates_series("NOT_A_SERIES") is False
    assert get_required_liquidity_rates_series() == series