"""Build JSON-friendly market risk observations from bundle summary inputs."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.market_risk.market_risk_engine import (
    calculate_composite_market_risk_score,
    determine_market_risk_label,
    map_breadth_participation_to_score,
    map_event_calendar_state_to_score,
    map_flows_positioning_state_to_score,
    map_macro_liquidity_state_to_score,
    map_news_sentiment_state_to_score,
    map_options_state_to_score,
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


def build_market_risk_observation(feature_summary, observation_date=None, timestamp=None, source="market_feature_bundle_summary"):
    payload = dict(feature_summary or {})
    observation_date_value = _normalize_timestamp(observation_date or payload.get("observation_date"))
    timestamp_value = _normalize_timestamp(timestamp or payload.get("timestamp"))

    component_states = {
        "volatility_state": payload.get("volatility_state"),
        "options_state": payload.get("macro_liquidity_state") or payload.get("options_state") or payload.get("options_regime_label"),
        "flows_positioning_state": payload.get("flows_positioning_state"),
        "event_calendar_state": payload.get("event_calendar_state"),
        "news_sentiment_state": payload.get("news_sentiment_state"),
        "breadth_participation_label": payload.get("breadth_participation_label"),
        "macro_liquidity_state": payload.get("macro_liquidity_state"),
        "price_states_by_symbol": dict(payload.get("price_states_by_symbol") or {}),
    }

    component_scores = {
        "volatility_risk_score": map_volatility_state_to_score(component_states["volatility_state"]),
        "options_risk_score": map_options_state_to_score(component_states["options_state"]),
        "positioning_risk_score": map_flows_positioning_state_to_score(component_states["flows_positioning_state"]),
        "event_risk_score": map_event_calendar_state_to_score(component_states["event_calendar_state"]),
        "sentiment_risk_score": map_news_sentiment_state_to_score(component_states["news_sentiment_state"]),
        "breadth_risk_score": map_breadth_participation_to_score(component_states["breadth_participation_label"]),
        "macro_liquidity_risk_score": map_macro_liquidity_state_to_score(component_states["macro_liquidity_state"]),
    }
    composite_score = calculate_composite_market_risk_score(component_scores)
    market_risk_label = determine_market_risk_label(composite_score, component_scores)

    metadata = _metadata_dict(payload)
    result = {
        "observation_date": observation_date_value,
        "timestamp": timestamp_value,
        "volatility_state": component_states["volatility_state"],
        "options_state": component_states["options_state"],
        "flows_positioning_state": component_states["flows_positioning_state"],
        "event_calendar_state": component_states["event_calendar_state"],
        "news_sentiment_state": component_states["news_sentiment_state"],
        "breadth_participation_label": component_states["breadth_participation_label"],
        "macro_liquidity_state": component_states["macro_liquidity_state"],
        "price_states_by_symbol": component_states["price_states_by_symbol"],
        "volatility_risk_score": component_scores["volatility_risk_score"],
        "options_risk_score": component_scores["options_risk_score"],
        "positioning_risk_score": component_scores["positioning_risk_score"],
        "event_risk_score": component_scores["event_risk_score"],
        "sentiment_risk_score": component_scores["sentiment_risk_score"],
        "breadth_risk_score": component_scores["breadth_risk_score"],
        "macro_liquidity_risk_score": component_scores["macro_liquidity_risk_score"],
        "composite_market_risk_score": composite_score,
        "market_risk_label": market_risk_label,
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

