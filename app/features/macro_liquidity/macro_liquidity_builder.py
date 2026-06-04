"""Build JSON-friendly macro liquidity observations from bundle summary inputs."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.macro_liquidity.macro_liquidity_engine import (
    calculate_composite_macro_liquidity_score,
    determine_macro_liquidity_label,
    map_breadth_participation_to_score,
    map_cross_asset_state_to_score,
    map_flows_positioning_state_to_score,
    map_liquidity_rates_state_to_score,
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


def build_macro_liquidity_observation(feature_summary, observation_date=None, timestamp=None, source="market_feature_bundle_summary"):
    payload = dict(feature_summary or {})
    observation_date_value = _normalize_timestamp(observation_date or payload.get("observation_date"))
    timestamp_value = _normalize_timestamp(timestamp or payload.get("timestamp"))

    component_states = {
        "liquidity_rates_state": payload.get("liquidity_rates_state"),
        "cross_asset_state": payload.get("cross_asset_state"),
        "flows_positioning_state": payload.get("flows_positioning_state"),
        "volatility_state": payload.get("volatility_state"),
        "breadth_participation_label": payload.get("breadth_participation_label"),
        "sector_rotation_state": payload.get("sector_rotation_state"),
    }
    component_scores = {
        "rates_liquidity_pressure_score": map_liquidity_rates_state_to_score(component_states["liquidity_rates_state"]),
        "cross_asset_confirmation_score": map_cross_asset_state_to_score(component_states["cross_asset_state"]),
        "positioning_liquidity_score": map_flows_positioning_state_to_score(component_states["flows_positioning_state"]),
        "volatility_liquidity_stress_score": map_volatility_state_to_score(component_states["volatility_state"]),
        "participation_confirmation_score": map_breadth_participation_to_score(component_states["breadth_participation_label"]),
        "sector_rotation_confirmation_score": map_sector_rotation_state_to_score(component_states["sector_rotation_state"]),
    }
    composite_score = calculate_composite_macro_liquidity_score(component_scores)
    macro_liquidity_label = determine_macro_liquidity_label(composite_score, component_scores)

    metadata = _metadata_dict(payload)
    result = {
        "observation_date": observation_date_value,
        "timestamp": timestamp_value,
        "liquidity_rates_state": component_states["liquidity_rates_state"],
        "cross_asset_state": component_states["cross_asset_state"],
        "flows_positioning_state": component_states["flows_positioning_state"],
        "volatility_state": component_states["volatility_state"],
        "breadth_participation_label": component_states["breadth_participation_label"],
        "sector_rotation_state": component_states["sector_rotation_state"],
        "rates_liquidity_pressure_score": component_scores["rates_liquidity_pressure_score"],
        "cross_asset_confirmation_score": component_scores["cross_asset_confirmation_score"],
        "positioning_liquidity_score": component_scores["positioning_liquidity_score"],
        "volatility_liquidity_stress_score": component_scores["volatility_liquidity_stress_score"],
        "participation_confirmation_score": component_scores["participation_confirmation_score"],
        "composite_macro_liquidity_score": composite_score,
        "macro_liquidity_label": macro_liquidity_label,
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
    return result

