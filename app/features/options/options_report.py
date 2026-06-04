"""Report helpers for options dry-run outputs."""

from __future__ import annotations


def build_options_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "symbol": payload.get("symbol"),
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "implied_volatility_level": payload.get("implied_volatility_level"),
        "realized_vs_implied_score": payload.get("realized_vs_implied_score"),
        "iv_rank_score": payload.get("iv_rank_score"),
        "put_call_pressure_score": payload.get("put_call_pressure_score"),
        "call_pressure_score": payload.get("call_pressure_score"),
        "gamma_pressure_score": payload.get("gamma_pressure_score"),
        "skew_pressure_score": payload.get("skew_pressure_score"),
        "iv_term_structure_score": payload.get("iv_term_structure_score"),
        "options_regime_label": payload.get("options_regime_label"),
        "safety_flags": {
            "no_db_writes": bool(payload.get("no_db_writes") is True),
            "no_vendor_calls": bool(payload.get("no_vendor_calls") is True),
            "no_scheduler_activation": bool(payload.get("no_scheduler_activation") is True),
        },
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
