"""Sector leadership ranking, leadership flag, and momentum helpers."""

from __future__ import annotations

from collections.abc import Mapping

from app.features.sector_rotation.relative_strength_engine import rank_symbols_by_metric


def build_rank_map(values_by_symbol: Mapping[str, float | int | None], descending: bool = True) -> dict[str, int]:
    """Build a deterministic rank map from symbol to rank.

    Rank 1 is strongest when ``descending=True``. Ties are broken alphabetically
    by symbol through the underlying ranking helper.
    """

    ranked_symbols = rank_symbols_by_metric(dict(values_by_symbol), descending=descending)
    return {symbol: index + 1 for index, symbol in enumerate(ranked_symbols)}


def calculate_rank_change(previous_rank: int | None, current_rank: int | None) -> int | None:
    """Return previous rank minus current rank.

    Positive values indicate improvement. Negative values indicate deterioration.
    """

    if previous_rank is None or current_rank is None:
        return None
    try:
        previous = int(previous_rank)
        current = int(current_rank)
    except (TypeError, ValueError):
        return None
    return previous - current


def calculate_rank_changes(
    previous_ranks: Mapping[str, int | None],
    current_ranks: Mapping[str, int | None],
) -> dict[str, int | None]:
    """Calculate rank changes for all symbols present in either mapping."""

    output: dict[str, int | None] = {}
    for symbol in sorted(set(previous_ranks) | set(current_ranks)):
        output[symbol] = calculate_rank_change(previous_ranks.get(symbol), current_ranks.get(symbol))
    return output


def calculate_momentum_score(
    relative_strength_5d: float | int | None = None,
    relative_strength_20d: float | int | None = None,
    relative_strength_60d: float | int | None = None,
    rank_change_5d: int | None = None,
    rank_change_20d: int | None = None,
) -> float | None:
    """Calculate a bounded deterministic momentum score in the range [-1, 1]."""

    weighted_components: list[float] = []

    def _normalize(value: float | int | None, scale: float) -> None:
        if value is None or scale <= 0:
            return
        try:
            normalized = float(value) / scale
        except (TypeError, ValueError):
            return
        weighted_components.append(max(-1.0, min(1.0, normalized)))

    _normalize(relative_strength_5d, 0.10)
    _normalize(relative_strength_20d, 0.15)
    _normalize(relative_strength_60d, 0.20)
    _normalize(rank_change_5d, 5.0)
    _normalize(rank_change_20d, 10.0)

    if not weighted_components:
        return None

    score = sum(weighted_components) / len(weighted_components)
    return max(-1.0, min(1.0, score))


def is_leadership_rank(rank: int | None, top_n: int = 3) -> bool:
    """Return True when the rank is within the leadership band."""

    if rank is None:
        return False
    try:
        rank_value = int(rank)
        top_value = int(top_n)
    except (TypeError, ValueError):
        return False
    return top_value > 0 and rank_value <= top_value


def is_deteriorating(
    rank_change_5d: int | None = None,
    rank_change_20d: int | None = None,
    relative_strength_5d: float | int | None = None,
    relative_strength_20d: float | int | None = None,
) -> bool:
    """Return True when rank and near-term relative strength weaken."""

    rank_weakening = False
    if rank_change_5d is not None or rank_change_20d is not None:
        rank_weakening = any(change is not None and change < 0 for change in (rank_change_5d, rank_change_20d))

    rs_weakening = False
    if relative_strength_5d is not None and relative_strength_20d is not None:
        try:
            rs_weakening = float(relative_strength_5d) < float(relative_strength_20d)
        except (TypeError, ValueError):
            rs_weakening = False

    return rank_weakening or rs_weakening


def build_sector_leadership_snapshot(relative_strength_by_window: Mapping[str, Mapping[str, float | int | None]]) -> dict[str, dict[str, float | int | bool | None]]:
    """Build a per-symbol leadership snapshot from relative strength windows.

    When prior ranks are unavailable, rank change fields fall back to ``None``.
    """

    window_order = ("5d", "20d", "60d")
    rank_maps: dict[str, dict[str, int]] = {}
    for window in window_order:
        values_by_symbol = dict(relative_strength_by_window.get(window, {}))
        rank_maps[window] = build_rank_map(values_by_symbol, descending=True)

    symbols = sorted({symbol for window_values in relative_strength_by_window.values() for symbol in window_values})
    output: dict[str, dict[str, float | int | bool | None]] = {}

    for symbol in symbols:
        rank_5d = rank_maps.get("5d", {}).get(symbol)
        rank_20d = rank_maps.get("20d", {}).get(symbol)
        rank_60d = rank_maps.get("60d", {}).get(symbol)
        rank_change_5d = calculate_rank_change(rank_20d, rank_5d) if rank_20d is not None else None
        rank_change_20d = calculate_rank_change(rank_60d, rank_20d) if rank_60d is not None else None
        rs_5d = relative_strength_by_window.get("5d", {}).get(symbol)
        rs_20d = relative_strength_by_window.get("20d", {}).get(symbol)
        rs_60d = relative_strength_by_window.get("60d", {}).get(symbol)

        output[symbol] = {
            "rank_5d": rank_5d,
            "rank_20d": rank_20d,
            "rank_60d": rank_60d,
            "rank_change_5d": rank_change_5d,
            "rank_change_20d": rank_change_20d,
            "momentum_score": calculate_momentum_score(
                relative_strength_5d=rs_5d,
                relative_strength_20d=rs_20d,
                relative_strength_60d=rs_60d,
                rank_change_5d=rank_change_5d,
                rank_change_20d=rank_change_20d,
            ),
            "leadership_flag": is_leadership_rank(rank_5d, top_n=3),
            "deterioration_flag": is_deteriorating(
                rank_change_5d=rank_change_5d,
                rank_change_20d=rank_change_20d,
                relative_strength_5d=rs_5d,
                relative_strength_20d=rs_20d,
            ),
        }
    return output
