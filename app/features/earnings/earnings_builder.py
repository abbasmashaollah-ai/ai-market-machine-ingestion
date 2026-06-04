"""Build JSON-friendly earnings observations from deterministic fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone

from app.features.earnings.earnings_engine import (
    calculate_days_since_earnings,
    calculate_days_to_earnings,
    calculate_earnings_quality_score,
    calculate_earnings_risk_score,
    calculate_estimate_revision_score,
    calculate_guidance_score,
    calculate_implied_vs_actual_move_score,
    calculate_post_earnings_reaction_score,
    calculate_pre_earnings_drift_score,
    calculate_surprise_score,
    determine_earnings_regime_label,
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
    result.setdefault("source_attribution", result.get("source", "fixture_earnings"))
    result.setdefault("dataset_version", "earnings_dry_run_v1")
    return result


def _default_timestamp(observation_date: str | None, suffix: str) -> str | None:
    if observation_date is None:
        return None
    return f"{observation_date}T00:00:00Z{suffix}"


def build_earnings_observation(symbol, earnings_payload, observation_date, timestamp=None, source="fixture_earnings"):
    payload = dict(earnings_payload or {})
    observation_date_value = _normalize_timestamp(observation_date)
    timestamp_value = _normalize_timestamp(timestamp)
    earnings_date = payload.get("earnings_date")
    days_to_earnings = calculate_days_to_earnings(observation_date_value, earnings_date)
    days_since_earnings = calculate_days_since_earnings(observation_date_value, earnings_date)

    eps_surprise_score = calculate_surprise_score(payload.get("eps_actual"), payload.get("eps_estimate"))
    revenue_surprise_score = calculate_surprise_score(payload.get("revenue_actual"), payload.get("revenue_estimate"))
    guidance_score = calculate_guidance_score(payload.get("guidance_direction"))
    estimate_revision_score = calculate_estimate_revision_score(payload.get("analyst_revision_trend"))
    pre_earnings_drift_score = calculate_pre_earnings_drift_score(payload.get("pre_earnings_price_change_5d"))
    post_earnings_reaction_score = calculate_post_earnings_reaction_score(
        payload.get("post_earnings_price_change_1d"),
        payload.get("post_earnings_price_change_5d"),
    )
    implied_vs_actual_move_score = calculate_implied_vs_actual_move_score(
        payload.get("implied_move_percent"),
        payload.get("actual_move_percent"),
    )

    component_scores = {
        "eps_surprise_score": eps_surprise_score,
        "revenue_surprise_score": revenue_surprise_score,
        "guidance_score": guidance_score,
        "estimate_revision_score": estimate_revision_score,
        "pre_earnings_drift_score": pre_earnings_drift_score,
        "post_earnings_reaction_score": post_earnings_reaction_score,
        "implied_vs_actual_move_score": implied_vs_actual_move_score,
    }
    earnings_quality_score = calculate_earnings_quality_score(component_scores)
    earnings_risk_score = calculate_earnings_risk_score(component_scores, days_to_earnings=days_to_earnings)
    earnings_regime_label = determine_earnings_regime_label(
        component_scores,
        days_to_earnings=days_to_earnings,
        days_since_earnings=days_since_earnings,
    )

    metadata = _metadata_dict(payload)
    source_attribution = metadata.get("source_attribution", source)
    dataset_version = metadata.get("dataset_version", "earnings_dry_run_v1")
    timestamp_anchor = observation_date_value or timestamp_value
    created_at = metadata.get("created_at") or _default_timestamp(timestamp_anchor, "")
    updated_at = metadata.get("updated_at") or _default_timestamp(timestamp_anchor, "")

    result = {
        "symbol": symbol,
        "observation_date": observation_date_value,
        "timestamp": timestamp_value,
        "earnings_date": earnings_date,
        "days_to_earnings": days_to_earnings,
        "days_since_earnings": days_since_earnings,
        "eps_surprise_score": eps_surprise_score,
        "revenue_surprise_score": revenue_surprise_score,
        "guidance_score": guidance_score,
        "estimate_revision_score": estimate_revision_score,
        "pre_earnings_drift_score": pre_earnings_drift_score,
        "post_earnings_reaction_score": post_earnings_reaction_score,
        "implied_vs_actual_move_score": implied_vs_actual_move_score,
        "earnings_quality_score": earnings_quality_score,
        "earnings_risk_score": earnings_risk_score,
        "earnings_regime_label": earnings_regime_label,
        "source": source,
        "source_attribution": source_attribution,
        "dataset_version": dataset_version,
        "created_at": created_at,
        "updated_at": updated_at,
        "quality_status": metadata["quality_status"],
        "certification_status": metadata["certification_status"],
        "freshness_status": metadata["freshness_status"],
        "lineage": metadata["lineage"],
        "evidence": {
            **metadata["evidence"],
            "source_payload": payload,
            "component_scores": component_scores,
        },
    }
    return result
