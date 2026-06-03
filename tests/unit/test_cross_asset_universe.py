from app.features.cross_asset.cross_asset_universe import get_cross_asset_groups, get_cross_asset_symbols, is_cross_asset_symbol


def test_universe_helpers() -> None:
    symbols = get_cross_asset_symbols()
    assert "SPY" in symbols
    assert "VIX" in symbols
    assert is_cross_asset_symbol("spy") is True
    assert is_cross_asset_symbol("not-a-symbol") is False
    groups = get_cross_asset_groups()
    assert "equity" in groups
    assert "volatility" in groups