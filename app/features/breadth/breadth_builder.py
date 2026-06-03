"""Build JSON-friendly breadth observations from close and volume histories."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.breadth.breadth_engine import (
    calculate_advancers_decliners_unchanged,
    calculate_advancing_declining_volume,
    calculate_breadth_score,
    calculate_new_highs_lows,
    calculate_participation_score,
    calculate_percent_above_moving_average,
)


def _normalize_date(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_dict(metadata: Mapping[str, object] | None) -> dict[str, object]:
    result = dict(metadata or {})
    result.setdefault("quality_status", "PENDING")
    result.setdefault("certification_status", "PENDING")
    result.setdefault("freshness_status", "PENDING")
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    return result


def build_breadth_observation(universe, close_history_by_symbol, volume_history_by_symbol, observation_date, timestamp=None, source="fixture_ohlcv"):
    universe_value = str(universe).strip()
    if not universe_value:
        raise ValueError("universe is required")

    previous_close_by_symbol: dict[str, float | None] = {}
    latest_close_by_symbol: dict[str, float | None] = {}
    latest_volume_by_symbol: dict[str, float | None] = {}

    for symbol, history in close_history_by_symbol.items():
        closes = [row["close"] if isinstance(row, Mapping) else row for row in history]
        closes = [value for value in closes if isinstance(value, (int, float))]
        if len(closes) < 2:
            continue
        previous_close_by_symbol[str(symbol).upper()] = float(closes[-2])
        latest_close_by_symbol[str(symbol).upper()] = float(closes[-1])

    for symbol, history in volume_history_by_symbol.items():
        volumes = [row["volume"] if isinstance(row, Mapping) else row for row in history]
        volumes = [value for value in volumes if isinstance(value, (int, float))]
        if not volumes:
            continue
        latest_volume_by_symbol[str(symbol).upper()] = float(volumes[-1])

    advancers, decliners, unchanged = calculate_advancers_decliners_unchanged(previous_close_by_symbol, latest_close_by_symbol)
    advancing_volume, declining_volume = calculate_advancing_declining_volume(previous_close_by_symbol, latest_close_by_symbol, latest_volume_by_symbol)
    percent_above_20d = calculate_percent_above_moving_average(close_history_by_symbol, 20)
    percent_above_50d = calculate_percent_above_moving_average(close_history_by_symbol, 50)
    percent_above_200d = calculate_percent_above_moving_average(close_history_by_symbol, 200)
    new_highs, new_lows = calculate_new_highs_lows(close_history_by_symbol, window=252)
    breadth_score = calculate_breadth_score(advancers, decliners, unchanged)
    participation_score = calculate_participation_score(percent_above_20d, percent_above_50d, percent_above_200d)
    payload = {
        "universe": universe_value,
        "observation_date": _normalize_date(observation_date),
        "timestamp": _normalize_date(timestamp),
        "advancers": advancers,
        "decliners": decliners,
        "unchanged": unchanged,
        "advancing_volume": advancing_volume,
        "declining_volume": declining_volume,
        "new_highs": new_highs,
        "new_lows": new_lows,
        "percent_above_20d": percent_above_20d,
        "percent_above_50d": percent_above_50d,
        "percent_above_200d": percent_above_200d,
        "breadth_score": breadth_score,
        "participation_score": participation_score,
        "source": source,
    }
    metadata_dict = _metadata_dict(None)
    payload.update(
        {
            "quality_status": metadata_dict["quality_status"],
            "certification_status": metadata_dict["certification_status"],
            "freshness_status": metadata_dict["freshness_status"],
            "lineage": metadata_dict["lineage"],
            "evidence": metadata_dict["evidence"],
        }
    )
    return payload
