"""Warehouse-shaped payload builders for sector rotation observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from collections.abc import Mapping, Sequence

from app.features.sector_rotation.sector_leadership_engine import build_sector_leadership_snapshot
from app.features.sector_rotation.sector_rotation_summary_engine import build_sector_rotation_daily_summary
from app.features.sector_rotation.sector_universe import SectorDefinition, SECTOR_ROTATION_UNIVERSE, get_spdr_sector_definitions


@dataclass(frozen=True, slots=True)
class SectorRotationBuildMetadata:
    universe: str = SECTOR_ROTATION_UNIVERSE
    source: str = "canonical_ohlcv"
    source_attribution: str = "ai-market-machine-ingestion"
    quality_status: str = "PENDING"
    certification_status: str = "PENDING"
    freshness_status: str = "PENDING"
    lineage: dict[str, object] = field(default_factory=dict)
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SectorPriceSnapshot:
    sector_symbol: str
    observation_date: str
    timestamp: str
    close: float | int | None


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("sector symbol is required")
    return normalized


def _normalize_date_value(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_to_dict(metadata: SectorRotationBuildMetadata | Mapping[str, object] | None) -> dict[str, object]:
    if metadata is None:
        metadata = SectorRotationBuildMetadata()
    if isinstance(metadata, SectorRotationBuildMetadata):
        return {
            "universe": metadata.universe,
            "source": metadata.source,
            "source_attribution": metadata.source_attribution,
            "quality_status": metadata.quality_status,
            "certification_status": metadata.certification_status,
            "freshness_status": metadata.freshness_status,
            "lineage": dict(metadata.lineage),
            "evidence": dict(metadata.evidence),
        }
    result = dict(metadata)
    result.setdefault("universe", SECTOR_ROTATION_UNIVERSE)
    result.setdefault("source", "canonical_ohlcv")
    result.setdefault("source_attribution", "ai-market-machine-ingestion")
    result.setdefault("quality_status", "PENDING")
    result.setdefault("certification_status", "PENDING")
    result.setdefault("freshness_status", "PENDING")
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    return result


def _window_value(values_by_window: Mapping[str | int, Mapping[str, object]], window: str, symbol: str) -> object | None:
    return values_by_window.get(window, {}).get(symbol)


def build_sector_rotation_observation(
    sector_definition: SectorDefinition,
    close_snapshot: SectorPriceSnapshot | Mapping[str, object],
    returns_by_window: Mapping[str | int, Mapping[str, object]] | None = None,
    relative_strength_by_window: Mapping[str | int, Mapping[str, object]] | None = None,
    leadership_snapshot: Mapping[str, Mapping[str, object]] | None = None,
    metadata: SectorRotationBuildMetadata | Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build one sector_rotation_observations row-shaped payload."""

    if close_snapshot is None:
        raise ValueError("close_snapshot is required")

    definition = sector_definition
    sector_symbol = _normalize_symbol(definition.symbol)

    if isinstance(close_snapshot, SectorPriceSnapshot):
        snapshot = {
            "sector_symbol": _normalize_symbol(close_snapshot.sector_symbol),
            "observation_date": _normalize_date_value(close_snapshot.observation_date),
            "timestamp": _normalize_date_value(close_snapshot.timestamp),
            "close": close_snapshot.close,
        }
    else:
        snapshot = {
            "sector_symbol": _normalize_symbol(str(close_snapshot.get("sector_symbol", sector_symbol))),
            "observation_date": _normalize_date_value(close_snapshot.get("observation_date")),
            "timestamp": _normalize_date_value(close_snapshot.get("timestamp")),
            "close": close_snapshot.get("close"),
        }

    if not snapshot["observation_date"]:
        raise ValueError("observation_date is required")

    leadership_snapshot = leadership_snapshot or {}
    sector_leadership = leadership_snapshot.get(sector_symbol, {})
    returns_by_window = returns_by_window or {}
    relative_strength_by_window = relative_strength_by_window or {}
    metadata_dict = _metadata_to_dict(metadata)

    payload = {
        "universe": metadata_dict["universe"],
        "sector": definition.name,
        "sector_symbol": sector_symbol,
        "observation_date": snapshot["observation_date"],
        "timestamp": snapshot["timestamp"],
        "close": snapshot["close"],
        "return_1d": _window_value(returns_by_window, "1d", sector_symbol),
        "return_5d": _window_value(returns_by_window, "5d", sector_symbol),
        "return_20d": _window_value(returns_by_window, "20d", sector_symbol),
        "return_60d": _window_value(returns_by_window, "60d", sector_symbol),
        "relative_strength_5d_vs_spy": _window_value(relative_strength_by_window, "5d", sector_symbol),
        "relative_strength_20d_vs_spy": _window_value(relative_strength_by_window, "20d", sector_symbol),
        "relative_strength_60d_vs_spy": _window_value(relative_strength_by_window, "60d", sector_symbol),
        "rank_5d": sector_leadership.get("rank_5d"),
        "rank_20d": sector_leadership.get("rank_20d"),
        "rank_60d": sector_leadership.get("rank_60d"),
        "rank_change_5d": sector_leadership.get("rank_change_5d"),
        "rank_change_20d": sector_leadership.get("rank_change_20d"),
        "momentum_score": sector_leadership.get("momentum_score"),
        "leadership_flag": sector_leadership.get("leadership_flag"),
        "deterioration_flag": sector_leadership.get("deterioration_flag"),
        "is_defensive_sector": definition.is_defensive_sector,
        "is_cyclical_sector": definition.is_cyclical_sector,
        "is_growth_sector": definition.is_growth_sector,
        "is_rate_sensitive_sector": definition.is_rate_sensitive_sector,
        "source": metadata_dict["source"],
        "source_attribution": metadata_dict["source_attribution"],
        "lineage": metadata_dict["lineage"],
        "quality_status": metadata_dict["quality_status"],
        "certification_status": metadata_dict["certification_status"],
        "freshness_status": metadata_dict["freshness_status"],
        "evidence": metadata_dict["evidence"],
    }
    return payload


def build_sector_rotation_observations(
    close_by_symbol: Mapping[str, float | int | None],
    returns_by_symbol_by_window: Mapping[str | int, Mapping[str, object]] | None = None,
    relative_strength_by_window: Mapping[str | int, Mapping[str, object]] | None = None,
    leadership_snapshot: Mapping[str, Mapping[str, object]] | None = None,
    metadata: SectorRotationBuildMetadata | Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    """Build sector rotation observation rows for all sector symbols."""

    returns_by_symbol_by_window = returns_by_symbol_by_window or {}
    relative_strength_by_window = relative_strength_by_window or {}
    leadership_snapshot = leadership_snapshot or {}
    metadata_dict = _metadata_to_dict(metadata)
    rows: list[dict[str, object]] = []

    for definition in get_spdr_sector_definitions():
        sector_symbol = _normalize_symbol(definition.symbol)
        close_value = close_by_symbol.get(sector_symbol)
        snapshot = SectorPriceSnapshot(
            sector_symbol=sector_symbol,
            observation_date=str(metadata_dict.get("observation_date", "")) or "",
            timestamp=str(metadata_dict.get("timestamp", "")) or "",
            close=close_value,
        )
        if not snapshot.observation_date:
            raise ValueError("metadata must include observation_date for sector observations")
        rows.append(
            build_sector_rotation_observation(
                definition,
                snapshot,
                returns_by_window=returns_by_symbol_by_window,
                relative_strength_by_window=relative_strength_by_window,
                leadership_snapshot=leadership_snapshot,
                metadata=metadata_dict,
            )
        )
    return rows


def build_sector_rotation_daily_summary_observation(
    summary_payload: Mapping[str, object],
    metadata: SectorRotationBuildMetadata | Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build one sector_rotation_daily_summary row-shaped payload."""

    if summary_payload is None:
        raise ValueError("summary_payload is required")
    metadata_dict = _metadata_to_dict(metadata)
    observation_date = _normalize_date_value(summary_payload.get("observation_date") if isinstance(summary_payload, Mapping) else None)
    timestamp = _normalize_date_value(summary_payload.get("timestamp") if isinstance(summary_payload, Mapping) else None)
    if not observation_date:
        raise ValueError("observation_date is required")
    payload = {
        "universe": metadata_dict["universe"],
        "observation_date": observation_date,
        "timestamp": timestamp,
        "descriptive_rotation_state": summary_payload.get("descriptive_rotation_state"),
        "risk_on_leadership_score": summary_payload.get("risk_on_leadership_score"),
        "defensive_leadership_score": summary_payload.get("defensive_leadership_score"),
        "leadership_concentration_score": summary_payload.get("leadership_concentration_score"),
        "sector_dispersion_score": summary_payload.get("sector_dispersion_score"),
        "broad_rotation_flag": summary_payload.get("broad_rotation_flag"),
        "narrow_rotation_flag": summary_payload.get("narrow_rotation_flag"),
        "improving_rotation_flag": summary_payload.get("improving_rotation_flag"),
        "deteriorating_rotation_flag": summary_payload.get("deteriorating_rotation_flag"),
        "top_sector_symbols": list(summary_payload.get("top_sector_symbols") or []),
        "bottom_sector_symbols": list(summary_payload.get("bottom_sector_symbols") or []),
        "source": metadata_dict["source"],
        "source_attribution": metadata_dict["source_attribution"],
        "lineage": metadata_dict["lineage"],
        "quality_status": metadata_dict["quality_status"],
        "certification_status": metadata_dict["certification_status"],
        "freshness_status": metadata_dict["freshness_status"],
        "evidence": metadata_dict["evidence"],
    }
    return payload
