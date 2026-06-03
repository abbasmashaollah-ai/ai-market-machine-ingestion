"""Cross-asset symbol universe helpers."""

from __future__ import annotations


CROSS_ASSET_GROUPS = {
    "equity": ("SPY", "QQQ", "IWM"),
    "credit": ("HYG",),
    "rates": ("TLT",),
    "commodities": ("GLD", "USO"),
    "dollar": ("DXY",),
    "volatility": ("VIX",),
}


def get_cross_asset_symbols() -> tuple[str, ...]:
    symbols: list[str] = []
    for group in CROSS_ASSET_GROUPS.values():
        for symbol in group:
            if symbol not in symbols:
                symbols.append(symbol)
    return tuple(symbols)


def get_cross_asset_groups() -> dict[str, tuple[str, ...]]:
    return dict(CROSS_ASSET_GROUPS)


def is_cross_asset_symbol(symbol) -> bool:
    return str(symbol).strip().upper() in get_cross_asset_symbols()