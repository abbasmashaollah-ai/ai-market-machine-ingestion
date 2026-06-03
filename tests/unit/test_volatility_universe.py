from app.features.volatility.volatility_universe import get_required_volatility_series, get_volatility_series, is_volatility_series


def test_universe_helpers() -> None:
    assert get_volatility_series() == ("VIX", "VVIX", "VXN", "RVX")
    assert get_required_volatility_series() == ("VIX", "VVIX", "VXN", "RVX")
    assert is_volatility_series("vix") is True
    assert is_volatility_series("spy") is False
