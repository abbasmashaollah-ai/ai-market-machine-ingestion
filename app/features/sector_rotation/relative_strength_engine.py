"""Pure return and relative-strength calculations for sector rotation."""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def calculate_period_return(start_close: float | int | None, end_close: float | int | None) -> float | None:
    """Calculate a simple period return.

    Returns None when either input is missing, non-positive, or invalid.
    """

    if start_close is None or end_close is None:
        return None
    try:
        start = float(start_close)
        end = float(end_close)
    except (TypeError, ValueError):
        return None
    if start <= 0 or end <= 0:
        return None
    return (end / start) - 1.0


def calculate_symbol_returns(
    close_history: Sequence[float | int | None],
    windows: Iterable[int] = (1, 5, 20, 60),
) -> dict[int, float | None]:
    """Calculate trailing returns for each requested window.

    The history is expected to be ordered oldest to newest. A 1-day return
    uses the last two closes, a 5-day return uses the close 5 periods ago
    relative to the latest close, and so on.
    """

    closes = list(close_history)
    results: dict[int, float | None] = {}
    if not closes:
        for window in windows:
            results[int(window)] = None
        return results

    for window in windows:
        period = int(window)
        if period <= 0:
            raise ValueError(f"window must be positive: {window!r}")
        if len(closes) <= period:
            results[period] = None
            continue
        start_close = closes[-(period + 1)]
        end_close = closes[-1]
        results[period] = calculate_period_return(start_close, end_close)
    return results


def calculate_relative_strength(sector_return: float | int | None, benchmark_return: float | int | None) -> float | None:
    """Calculate relative strength as sector return minus benchmark return."""

    if sector_return is None or benchmark_return is None:
        return None
    try:
        return float(sector_return) - float(benchmark_return)
    except (TypeError, ValueError):
        return None


def calculate_relative_strength_map(
    sector_returns_by_symbol: dict[str, dict[int, float | int | None]],
    benchmark_returns: dict[int, float | int | None],
) -> dict[str, dict[int, float | None]]:
    """Calculate relative strength maps for each symbol and window."""

    output: dict[str, dict[int, float | None]] = {}
    for symbol, returns_by_window in sector_returns_by_symbol.items():
        window_map: dict[int, float | None] = {}
        for window, sector_return in returns_by_window.items():
            benchmark_return = benchmark_returns.get(int(window))
            window_map[int(window)] = calculate_relative_strength(sector_return, benchmark_return)
        output[symbol] = window_map
    return output


def rank_symbols_by_metric(values_by_symbol: dict[str, float | int | None], descending: bool = True) -> list[str]:
    """Rank symbols by metric value, tie-breaking alphabetically by symbol."""

    sortable: list[tuple[str, float]] = []
    for symbol, value in values_by_symbol.items():
        if value is None:
            continue
        try:
            sortable.append((symbol, float(value)))
        except (TypeError, ValueError):
            continue

    sortable.sort(key=lambda item: (item[0]))
    sortable.sort(key=lambda item: item[1], reverse=descending)
    return [symbol for symbol, _ in sortable]
