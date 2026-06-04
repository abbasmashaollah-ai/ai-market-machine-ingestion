"""Builder for dry-run fundamentals observations."""

from __future__ import annotations

from datetime import datetime, timezone

from .fundamentals_engine import (
    calculate_balance_sheet_score,
    calculate_cash_flow_score,
    calculate_composite_fundamental_score,
    calculate_growth_score,
    calculate_profitability_score,
    calculate_valuation_score,
    determine_fundamental_quality_label,
)


def _normalize_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def build_fundamental_observation(symbol, financials, observation_date, timestamp=None, source="fixture_fundamentals"):
    payload = dict(financials or {})
    source_attribution = payload.get("source_attribution") or source
    dataset_version = payload.get("dataset_version") or "fundamentals_dry_run_v1"
    created_at = payload.get("created_at") or f"{observation_date}T00:00:00Z"
    updated_at = payload.get("updated_at") or f"{observation_date}T00:00:00Z"
    growth_score = calculate_growth_score(payload)
    profitability_score = calculate_profitability_score(payload)
    balance_sheet_score = calculate_balance_sheet_score(payload)
    valuation_score = calculate_valuation_score(payload)
    cash_flow_score = calculate_cash_flow_score(payload)
    component_scores = {
        "growth_score": growth_score,
        "profitability_score": profitability_score,
        "balance_sheet_score": balance_sheet_score,
        "valuation_score": valuation_score,
        "cash_flow_score": cash_flow_score,
    }
    composite = calculate_composite_fundamental_score(component_scores)
    quality_label = determine_fundamental_quality_label(composite, component_scores)
    return {
        "symbol": str(symbol).upper(),
        "observation_date": str(observation_date),
        "timestamp": _normalize_timestamp(timestamp),
        **component_scores,
        "composite_fundamental_score": composite,
        "fundamental_quality_label": quality_label,
        "source": source,
        "source_attribution": source_attribution,
        "dataset_version": dataset_version,
        "created_at": created_at,
        "updated_at": updated_at,
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {"source_payload": payload},
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
