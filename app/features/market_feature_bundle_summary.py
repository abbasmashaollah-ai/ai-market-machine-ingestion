"""Compact evidence summary helpers for market feature bundle dry runs."""

from __future__ import annotations

from collections.abc import Mapping


def _as_int(value: object):
    return value if isinstance(value, int) else None


def _price_states_by_symbol(bundle: Mapping[str, object]) -> dict[str, object]:
    prices = bundle.get("prices")
    if not isinstance(prices, Mapping):
        return {}
    return {
        symbol: report.get("price_trend_state")
        for symbol, report in (prices.get("reports_by_symbol") or {}).items()
        if isinstance(symbol, str) and isinstance(report, Mapping)
    }


def _section_counts(section: Mapping[str, object], accepted_key: str, rejected_key: str) -> dict[str, int | None]:
    return {
        "accepted": _as_int(section.get(accepted_key)),
        "rejected": _as_int(section.get(rejected_key)),
    }


def build_market_feature_bundle_summary(bundle):
    payload = dict(bundle or {})
    prices = payload.get("prices") if isinstance(payload.get("prices"), Mapping) else {}
    breadth = payload.get("breadth") if isinstance(payload.get("breadth"), Mapping) else {}
    sector_rotation = payload.get("sector_rotation") if isinstance(payload.get("sector_rotation"), Mapping) else {}
    cross_asset = payload.get("cross_asset") if isinstance(payload.get("cross_asset"), Mapping) else {}

    breadth_label = breadth.get("participation_label") or (breadth.get("report") or {}).get("participation_label") if isinstance(breadth.get("report"), Mapping) else breadth.get("participation_label")
    if isinstance(breadth_label, Mapping):
        breadth_label = None
    sector_state = sector_rotation.get("descriptive_rotation_state") or (sector_rotation.get("report") or {}).get("descriptive_rotation_state") if isinstance(sector_rotation.get("report"), Mapping) else sector_rotation.get("descriptive_rotation_state")
    if isinstance(sector_state, Mapping):
        sector_state = None
    cross_state = cross_asset.get("descriptive_intermarket_state") or (cross_asset.get("report") or {}).get("descriptive_intermarket_state") if isinstance(cross_asset.get("report"), Mapping) else cross_asset.get("descriptive_intermarket_state")
    if isinstance(cross_state, Mapping):
        cross_state = None

    feature_sections_present = {
        "prices": isinstance(prices, Mapping),
        "breadth": isinstance(breadth, Mapping),
        "sector_rotation": isinstance(sector_rotation, Mapping),
        "cross_asset": isinstance(cross_asset, Mapping),
    }

    accepted_counts_by_section = {
        "prices": _section_counts(prices, "accepted_count", "rejected_count"),
        "breadth": _section_counts(breadth, "accepted_count", "rejected_count"),
        "sector_rotation": {
            "accepted": _as_int(sector_rotation.get("accepted_observation_count")),
            "rejected": _as_int(sector_rotation.get("rejected_observation_count")),
            "accepted_summary": _as_int(sector_rotation.get("accepted_summary_count")),
            "rejected_summary": _as_int(sector_rotation.get("rejected_summary_count")),
        },
        "cross_asset": _section_counts(cross_asset, "accepted_count", "rejected_count"),
    }

    total_warnings = 0
    warnings = payload.get("warnings")
    if isinstance(warnings, list):
        total_warnings += len(warnings)
    for section in (prices, breadth, sector_rotation, cross_asset):
        section_warnings = section.get("warnings") if isinstance(section, Mapping) else None
        if isinstance(section_warnings, list):
            total_warnings += len(section_warnings)

    summary = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "price_states_by_symbol": _price_states_by_symbol(payload),
        "breadth_participation_label": breadth_label,
        "sector_rotation_state": sector_state,
        "cross_asset_state": cross_state,
        "total_warnings": total_warnings,
        "feature_sections_present": feature_sections_present,
        "accepted_counts_by_section": accepted_counts_by_section,
        "rejected_counts_by_section": {
            "prices": accepted_counts_by_section["prices"]["rejected"],
            "breadth": accepted_counts_by_section["breadth"]["rejected"],
            "sector_rotation": accepted_counts_by_section["sector_rotation"]["rejected"],
            "cross_asset": accepted_counts_by_section["cross_asset"]["rejected"],
        },
        "safety_flags": {
            "no_db_writes": bool(payload.get("no_db_writes") is True),
            "no_vendor_calls": bool(payload.get("no_vendor_calls") is True),
            "no_live_api_calls": bool(payload.get("no_live_api_calls") is True),
            "no_scheduler_activation": bool(payload.get("no_scheduler_activation") is True),
        },
    }

    states = [
        str(summary["breadth_participation_label"] or ""),
        str(summary["sector_rotation_state"] or ""),
        str(summary["cross_asset_state"] or ""),
    ]
    if all(state for state in states):
        if any("RISK_OFF" in state for state in states):
            summary["descriptive_market_evidence_state"] = "RISK_OFF_EVIDENCE"
        elif any("RISK_ON" in state for state in states):
            summary["descriptive_market_evidence_state"] = "RISK_ON_EVIDENCE"
        elif any("MIXED" in state for state in states):
            summary["descriptive_market_evidence_state"] = "MIXED_EVIDENCE"
        else:
            summary["descriptive_market_evidence_state"] = "INSUFFICIENT_EVIDENCE"
    else:
        summary["descriptive_market_evidence_state"] = "INSUFFICIENT_EVIDENCE"

    return summary