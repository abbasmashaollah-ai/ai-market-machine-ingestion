"""Build JSON-friendly market regime observations from bundle summary inputs."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.market_regime.market_regime_engine import (
    calculate_composite_market_regime_score,
    determine_market_regime_label,
    map_breadth_participation_to_score,
    map_cross_asset_state_to_score,
    map_macro_liquidity_state_to_score,
    map_market_risk_state_to_score,
    map_price_states_to_trend_score,
    map_sector_rotation_state_to_score,
    map_volatility_state_to_score,
)


def _normalize_timestamp(value: date | datetime | str | None) -> str | None:
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


def build_market_regime_observation(feature_summary, observation_date=None, timestamp=None, source="market_feature_bundle_summary"):
    payload = dict(feature_summary or {})
    observation_date_value = _normalize_timestamp(observation_date or payload.get("observation_date"))
    timestamp_value = _normalize_timestamp(timestamp or payload.get("timestamp"))

    component_states = {
        "macro_liquidity_state": payload.get("macro_liquidity_state"),
        "market_risk_state": payload.get("market_risk_state"),
        "breadth_participation_label": payload.get("breadth_participation_label"),
        "sector_rotation_state": payload.get("sector_rotation_state"),
        "cross_asset_state": payload.get("cross_asset_state"),
        "volatility_state": payload.get("volatility_state"),
        "price_states_by_symbol": dict(payload.get("price_states_by_symbol") or {}),
    }
    component_scores = {
        "liquidity_regime_score": map_macro_liquidity_state_to_score(component_states["macro_liquidity_state"]),
        "risk_regime_score": map_market_risk_state_to_score(component_states["market_risk_state"]),
        "participation_regime_score": map_breadth_participation_to_score(component_states["breadth_participation_label"]),
        "rotation_regime_score": map_sector_rotation_state_to_score(component_states["sector_rotation_state"]),
        "cross_asset_regime_score": map_cross_asset_state_to_score(component_states["cross_asset_state"]),
        "trend_regime_score": map_price_states_to_trend_score(component_states["price_states_by_symbol"]),
        "volatility_regime_score": map_volatility_state_to_score(component_states["volatility_state"]),
    }
    composite_score = calculate_composite_market_regime_score(component_scores)
    market_regime_label = determine_market_regime_label(composite_score, component_scores)

    metadata = _metadata_dict(payload)
    return {
        "observation_date": observation_date_value,
        "timestamp": timestamp_value,
        "macro_liquidity_state": component_states["macro_liquidity_state"],
        "market_risk_state": component_states["market_risk_state"],
        "breadth_participation_label": component_states["breadth_participation_label"],
        "sector_rotation_state": component_states["sector_rotation_state"],
        "cross_asset_state": component_states["cross_asset_state"],
        "volatility_state": component_states["volatility_state"],
        "price_states_by_symbol": component_states["price_states_by_symbol"],
        "liquidity_regime_score": component_scores["liquidity_regime_score"],
        "risk_regime_score": component_scores["risk_regime_score"],
        "participation_regime_score": component_scores["participation_regime_score"],
        "rotation_regime_score": component_scores["rotation_regime_score"],
        "cross_asset_regime_score": component_scores["cross_asset_regime_score"],
        "trend_regime_score": component_scores["trend_regime_score"],
        "volatility_regime_score": component_scores["volatility_regime_score"],
        "composite_market_regime_score": composite_score,
        "market_regime_label": market_regime_label,
        "source": source,
        "quality_status": metadata["quality_status"],
        "certification_status": metadata["certification_status"],
        "freshness_status": metadata["freshness_status"],
        "lineage": metadata["lineage"],
        "evidence": {
            **metadata["evidence"],
            "source_payload": payload,
            "component_states": component_states,
            "component_scores": component_scores,
        },
    }

