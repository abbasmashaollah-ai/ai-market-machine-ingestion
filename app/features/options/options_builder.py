"""Builder for dry-run options observations."""

from __future__ import annotations

from datetime import datetime, timezone

from .options_engine import (
    calculate_call_pressure_score,
    calculate_gamma_pressure_score,
    calculate_implied_volatility_level,
    calculate_iv_rank_score,
    calculate_iv_term_structure_score,
    calculate_put_call_pressure_score,
    calculate_realized_vs_implied_score,
    calculate_skew_pressure_score,
    determine_options_regime_label,
)


def _normalize_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def build_options_observation(symbol, metrics, observation_date, timestamp=None, source="fixture_options"):
    payload = dict(metrics or {})
    underlying_symbol = str(payload.get("underlying_symbol") or symbol).upper()
    expiration_date = payload.get("expiration_date")
    total_volume = payload.get("total_volume")
    total_open_interest = payload.get("total_open_interest")
    implied_volatility_level = calculate_implied_volatility_level(payload)
    realized_vs_implied_score = calculate_realized_vs_implied_score(payload)
    iv_rank_score = calculate_iv_rank_score(payload)
    put_call_pressure_score = calculate_put_call_pressure_score(payload)
    call_pressure_score = calculate_call_pressure_score(payload)
    gamma_pressure_score = calculate_gamma_pressure_score(payload)
    skew_pressure_score = calculate_skew_pressure_score(payload)
    iv_term_structure_score = calculate_iv_term_structure_score(payload)
    component_scores = {
        "implied_volatility_level": implied_volatility_level,
        "realized_vs_implied_score": realized_vs_implied_score,
        "iv_rank_score": iv_rank_score,
        "put_call_pressure_score": put_call_pressure_score,
        "call_pressure_score": call_pressure_score,
        "gamma_pressure_score": gamma_pressure_score,
        "skew_pressure_score": skew_pressure_score,
        "iv_term_structure_score": iv_term_structure_score,
    }
    options_regime_label = determine_options_regime_label(component_scores)
    return {
        "symbol": str(symbol).upper(),
        "underlying_symbol": underlying_symbol,
        "expiration_date": str(expiration_date) if expiration_date is not None else None,
        "total_volume": total_volume,
        "total_open_interest": total_open_interest,
        "observation_date": str(observation_date),
        "timestamp": _normalize_timestamp(timestamp),
        **component_scores,
        "options_regime_label": options_regime_label,
        "source": source,
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {"source_payload": payload},
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
