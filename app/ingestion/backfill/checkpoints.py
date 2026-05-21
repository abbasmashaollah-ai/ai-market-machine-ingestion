from __future__ import annotations


def build_checkpoint_key(
    *,
    vendor: str,
    dataset: str,
    symbol: str | None = None,
    timeframe: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    parts = [vendor, dataset]
    if symbol:
        parts.append(symbol)
    if timeframe:
        parts.append(timeframe)
    if start_date:
        parts.append(start_date)
    if end_date:
        parts.append(end_date)
    return ":".join(parts)
