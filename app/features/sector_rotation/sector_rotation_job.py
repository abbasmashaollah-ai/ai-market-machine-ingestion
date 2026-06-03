"""Dry-run sector rotation pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from collections.abc import Mapping, Sequence

from app.features.sector_rotation.relative_strength_engine import (
    calculate_relative_strength_map,
    calculate_symbol_returns,
)
from app.features.sector_rotation.sector_leadership_engine import build_sector_leadership_snapshot
from app.features.sector_rotation.sector_rotation_observation_builder import (
    SectorRotationBuildMetadata,
    build_sector_rotation_daily_summary_observation,
    build_sector_rotation_observations,
)
from app.features.sector_rotation.sector_rotation_summary_engine import build_sector_rotation_daily_summary
from app.features.sector_rotation.sector_rotation_writer import SectorRotationMockWriter, SectorRotationWriterResult, write_sector_rotation_payloads
from app.features.sector_rotation.sector_universe import SPY_BENCHMARK, get_sector_symbols


@dataclass(frozen=True, slots=True)
class SectorRotationDryRunResult:
    observation_rows: tuple[dict[str, object], ...]
    summary_row: dict[str, object]
    writer_result: SectorRotationWriterResult
    accepted_observation_count: int
    accepted_summary_count: int
    rejected_observation_count: int
    rejected_summary_count: int
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol is required")
    return normalized


def _normalize_timestamp(timestamp: datetime | date | str | None) -> str | None:
    if timestamp is None:
        return None
    if isinstance(timestamp, datetime):
        return timestamp.astimezone(timezone.utc).isoformat()
    if isinstance(timestamp, date):
        return datetime(timestamp.year, timestamp.month, timestamp.day, tzinfo=timezone.utc).isoformat()
    return str(timestamp)


def _build_close_snapshot(price_history_by_symbol: Mapping[str, Sequence[float | int | None]]) -> dict[str, float | int | None]:
    close_snapshot: dict[str, float | int | None] = {}
    for symbol, history in price_history_by_symbol.items():
        normalized_symbol = _normalize_symbol(symbol)
        if not history:
            close_snapshot[normalized_symbol] = None
            continue
        close_snapshot[normalized_symbol] = history[-1]
    return close_snapshot


def _window_label(window: int | str) -> str:
    if isinstance(window, int):
        return f"{window}d"
    window_str = str(window)
    return window_str if window_str.endswith("d") else f"{window_str}d"


def _transpose_window_map(symbol_to_window_values: Mapping[str, Mapping[int, float | None]]) -> dict[str, dict[str, float | None]]:
    transposed: dict[str, dict[str, float | None]] = {}
    for symbol, window_values in symbol_to_window_values.items():
        normalized_symbol = _normalize_symbol(symbol)
        for window, value in window_values.items():
            transposed.setdefault(_window_label(window), {})[normalized_symbol] = value
    return transposed


def _latest_required_length(price_history_by_symbol: Mapping[str, Sequence[float | int | None]]) -> int:
    return max((len(history) for history in price_history_by_symbol.values()), default=0)


def _validate_price_histories(price_history_by_symbol: Mapping[str, Sequence[float | int | None]]) -> tuple[list[str], list[str]]:
    normalized_symbols = {_normalize_symbol(symbol) for symbol in price_history_by_symbol}

    if SPY_BENCHMARK not in normalized_symbols:
        raise ValueError("SPY benchmark is required for sector rotation dry run")

    sector_symbols = [symbol for symbol in get_sector_symbols() if symbol in normalized_symbols]
    if not sector_symbols:
        raise ValueError("at least one sector symbol is required for sector rotation dry run")

    warnings: list[str] = []
    required_length = 61
    for symbol in sector_symbols:
        if len(price_history_by_symbol.get(symbol, [])) < required_length:
            warnings.append(f"insufficient_history_for_60d_outputs:{symbol}")
    return sector_symbols, warnings


def run_sector_rotation_dry_run(
    price_history_by_symbol: Mapping[str, Sequence[float | int | None]],
    observation_date: date | datetime | str,
    timestamp: datetime | str | None = None,
    writer: SectorRotationMockWriter | None = None,
    metadata: SectorRotationBuildMetadata | Mapping[str, object] | None = None,
) -> SectorRotationDryRunResult:
    """Run the full sector rotation feature flow in memory only."""

    sector_symbols, warnings = _validate_price_histories(price_history_by_symbol)
    normalized_histories = {_normalize_symbol(symbol): list(history) for symbol, history in price_history_by_symbol.items()}
    normalized_observation_date = observation_date.isoformat() if isinstance(observation_date, date) and not isinstance(observation_date, datetime) else str(observation_date)
    normalized_timestamp = _normalize_timestamp(timestamp)

    closes_by_symbol = _build_close_snapshot(normalized_histories)
    returns_by_symbol_by_window: dict[str, dict[str, float | None]] = {}
    for symbol, history in normalized_histories.items():
        returns_by_symbol_by_window[symbol] = calculate_symbol_returns(history)

    spy_returns = returns_by_symbol_by_window.get(SPY_BENCHMARK, {})
    relative_strength_by_window = calculate_relative_strength_map(
        {symbol: returns_by_symbol_by_window[symbol] for symbol in sector_symbols},
        spy_returns,
    )

    relative_strength_by_window_transposed = _transpose_window_map(relative_strength_by_window)
    returns_by_window_transposed = _transpose_window_map(returns_by_symbol_by_window)

    leadership_snapshot = build_sector_leadership_snapshot(relative_strength_by_window_transposed)

    symbol_scores = relative_strength_by_window_transposed.get("20d", relative_strength_by_window_transposed.get("5d", {}))
    summary_payload = build_sector_rotation_daily_summary(
        symbol_scores,
        leadership_snapshot=leadership_snapshot,
    )
    summary_payload = build_sector_rotation_daily_summary_observation(
        {
            "observation_date": normalized_observation_date,
            "timestamp": normalized_timestamp,
            **summary_payload,
        },
        metadata=metadata,
    )

    observation_rows = build_sector_rotation_observations(
        {symbol: closes_by_symbol.get(symbol) for symbol in normalized_histories},
        returns_by_symbol_by_window=returns_by_window_transposed,
        relative_strength_by_window=relative_strength_by_window_transposed,
        leadership_snapshot=leadership_snapshot,
        metadata={
            "observation_date": normalized_observation_date,
            "timestamp": normalized_timestamp,
            **({} if metadata is None else (dict(metadata) if isinstance(metadata, Mapping) else {})),
        },
    )
    observation_rows = tuple(row for row in observation_rows if row["sector_symbol"] != SPY_BENCHMARK)

    writer = writer or SectorRotationMockWriter()
    writer_result = write_sector_rotation_payloads(observation_rows, [summary_payload], writer=writer)

    return SectorRotationDryRunResult(
        observation_rows=observation_rows,
        summary_row=summary_payload,
        writer_result=writer_result,
        accepted_observation_count=writer_result.accepted_observation_count,
        accepted_summary_count=writer_result.accepted_summary_count,
        rejected_observation_count=writer_result.rejected_observation_count,
        rejected_summary_count=writer_result.rejected_summary_count,
        warnings=tuple(warnings) + tuple(writer_result.warnings),
    )
