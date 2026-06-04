"""Compact evidence summary helpers for market feature bundle dry runs."""

from __future__ import annotations

from collections.abc import Mapping


def _as_int(value: object) -> int | None:
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


def _non_empty_string(value: object) -> str | None:
    return value if isinstance(value, str) and bool(value.strip()) else None


def build_market_feature_bundle_summary(bundle):
    payload = dict(bundle or {})
    prices = payload.get("prices") if isinstance(payload.get("prices"), Mapping) else {}
    breadth = payload.get("breadth") if isinstance(payload.get("breadth"), Mapping) else {}
    sector_rotation = payload.get("sector_rotation") if isinstance(payload.get("sector_rotation"), Mapping) else {}
    cross_asset = payload.get("cross_asset") if isinstance(payload.get("cross_asset"), Mapping) else {}
    liquidity_rates = payload.get("liquidity_rates") if isinstance(payload.get("liquidity_rates"), Mapping) else {}
    volatility = payload.get("volatility") if isinstance(payload.get("volatility"), Mapping) else {}
    event_calendar = payload.get("event_calendar") if isinstance(payload.get("event_calendar"), Mapping) else {}
    news_sentiment = payload.get("news_sentiment") if isinstance(payload.get("news_sentiment"), Mapping) else {}
    earnings = payload.get("earnings") if isinstance(payload.get("earnings"), Mapping) else {}
    macro_liquidity = payload.get("macro_liquidity") if isinstance(payload.get("macro_liquidity"), Mapping) else {}
    market_risk = payload.get("market_risk") if isinstance(payload.get("market_risk"), Mapping) else {}
    fundamentals = payload.get("fundamentals") if isinstance(payload.get("fundamentals"), Mapping) else {}
    flows_positioning = payload.get("flows_positioning") if isinstance(payload.get("flows_positioning"), Mapping) else {}
    options = payload.get("options") if isinstance(payload.get("options"), Mapping) else {}

    breadth_label = _non_empty_string(breadth.get("participation_label")) or _non_empty_string((breadth.get("report") or {}).get("participation_label") if isinstance(breadth.get("report"), Mapping) else None)
    sector_state = _non_empty_string(sector_rotation.get("descriptive_rotation_state")) or _non_empty_string((sector_rotation.get("report") or {}).get("descriptive_rotation_state") if isinstance(sector_rotation.get("report"), Mapping) else None)
    cross_state = _non_empty_string(cross_asset.get("descriptive_intermarket_state")) or _non_empty_string((cross_asset.get("report") or {}).get("descriptive_intermarket_state") if isinstance(cross_asset.get("report"), Mapping) else None)
    liquidity_state = _non_empty_string(liquidity_rates.get("liquidity_regime_label")) or _non_empty_string((liquidity_rates.get("report") or {}).get("liquidity_regime_label") if isinstance(liquidity_rates.get("report"), Mapping) else None)
    volatility_state = _non_empty_string(volatility.get("volatility_regime_label")) or _non_empty_string((volatility.get("report") or {}).get("volatility_regime_label") if isinstance(volatility.get("report"), Mapping) else None)
    event_calendar_state = _non_empty_string(event_calendar.get("event_risk_label")) or _non_empty_string((event_calendar.get("report") or {}).get("event_risk_label") if isinstance(event_calendar.get("report"), Mapping) else None)
    news_sentiment_state = _non_empty_string(news_sentiment.get("sentiment_regime_label")) or _non_empty_string((news_sentiment.get("report") or {}).get("sentiment_regime_label") if isinstance(news_sentiment.get("report"), Mapping) else None)
    earnings_labels = earnings.get("earnings_regime_labels_by_symbol") if isinstance(earnings.get("earnings_regime_labels_by_symbol"), Mapping) else {}
    macro_liquidity_state = _non_empty_string(macro_liquidity.get("macro_liquidity_label")) or _non_empty_string((macro_liquidity.get("report") or {}).get("macro_liquidity_label") if isinstance(macro_liquidity.get("report"), Mapping) else None)
    market_risk_state = _non_empty_string(market_risk.get("market_risk_label")) or _non_empty_string((market_risk.get("report") or {}).get("market_risk_label") if isinstance(market_risk.get("report"), Mapping) else None)
    fundamental_labels = fundamentals.get("fundamental_quality_labels_by_symbol") if isinstance(fundamentals.get("fundamental_quality_labels_by_symbol"), Mapping) else {}
    flows_positioning_state = _non_empty_string(flows_positioning.get("flow_regime_label")) or _non_empty_string((flows_positioning.get("report") or {}).get("flow_regime_label") if isinstance(flows_positioning.get("report"), Mapping) else None)
    options_regime_label = _non_empty_string(options.get("options_regime_label")) or _non_empty_string((options.get("report") or {}).get("options_regime_label") if isinstance(options.get("report"), Mapping) else None)

    feature_sections_present = {
        "prices": isinstance(prices, Mapping),
        "breadth": isinstance(breadth, Mapping),
        "sector_rotation": isinstance(sector_rotation, Mapping),
        "cross_asset": isinstance(cross_asset, Mapping),
        "liquidity_rates": isinstance(liquidity_rates, Mapping),
        "volatility": isinstance(volatility, Mapping),
        "event_calendar": isinstance(event_calendar, Mapping),
        "news_sentiment": isinstance(news_sentiment, Mapping),
        "earnings": isinstance(earnings, Mapping),
        "macro_liquidity": isinstance(macro_liquidity, Mapping),
        "market_risk": isinstance(market_risk, Mapping),
        "fundamentals": isinstance(fundamentals, Mapping),
        "flows_positioning": isinstance(flows_positioning, Mapping),
        "options": isinstance(options, Mapping),
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
        "liquidity_rates": _section_counts(liquidity_rates, "accepted_count", "rejected_count"),
        "volatility": _section_counts(volatility, "accepted_count", "rejected_count"),
        "event_calendar": _section_counts(event_calendar, "accepted_count", "rejected_count"),
        "news_sentiment": _section_counts(news_sentiment, "accepted_count", "rejected_count"),
        "earnings": _section_counts(earnings, "accepted_count", "rejected_count"),
        "macro_liquidity": _section_counts(macro_liquidity, "accepted_count", "rejected_count"),
        "market_risk": _section_counts(market_risk, "accepted_count", "rejected_count"),
        "fundamentals": _section_counts(fundamentals, "accepted_count", "rejected_count"),
        "flows_positioning": _section_counts(flows_positioning, "accepted_count", "rejected_count"),
        "options": _section_counts(options, "accepted_count", "rejected_count"),
    }

    warnings = payload.get("warnings")
    total_warnings = len(warnings) if isinstance(warnings, list) else 0

    summary = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "price_states_by_symbol": _price_states_by_symbol(payload),
        "breadth_participation_label": breadth_label,
        "sector_rotation_state": sector_state,
        "cross_asset_state": cross_state,
        "liquidity_rates_state": liquidity_state,
        "volatility_state": volatility_state,
        "event_calendar_state": event_calendar_state,
        "news_sentiment_state": news_sentiment_state,
        "earnings_regime_labels_by_symbol": dict(earnings_labels),
        "macro_liquidity_state": macro_liquidity_state,
        "market_risk_state": market_risk_state,
        "fundamental_quality_labels_by_symbol": dict(fundamental_labels),
        "flows_positioning_state": flows_positioning_state,
        "options_regime_labels_by_symbol": dict(options.get("options_regime_labels_by_symbol") or {}),
        "total_warnings": total_warnings,
        "feature_sections_present": feature_sections_present,
        "accepted_counts_by_section": accepted_counts_by_section,
        "rejected_counts_by_section": {
            "prices": accepted_counts_by_section["prices"]["rejected"],
            "breadth": accepted_counts_by_section["breadth"]["rejected"],
            "sector_rotation": accepted_counts_by_section["sector_rotation"]["rejected"],
            "cross_asset": accepted_counts_by_section["cross_asset"]["rejected"],
            "liquidity_rates": accepted_counts_by_section["liquidity_rates"]["rejected"],
            "volatility": accepted_counts_by_section["volatility"]["rejected"],
            "event_calendar": accepted_counts_by_section["event_calendar"]["rejected"],
            "news_sentiment": accepted_counts_by_section["news_sentiment"]["rejected"],
            "earnings": accepted_counts_by_section["earnings"]["rejected"],
            "macro_liquidity": accepted_counts_by_section["macro_liquidity"]["rejected"],
            "market_risk": accepted_counts_by_section["market_risk"]["rejected"],
            "fundamentals": accepted_counts_by_section["fundamentals"]["rejected"],
            "flows_positioning": accepted_counts_by_section["flows_positioning"]["rejected"],
            "options": accepted_counts_by_section["options"]["rejected"],
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
        str(summary["liquidity_rates_state"] or ""),
        str(summary["volatility_state"] or ""),
        str(summary["event_calendar_state"] or ""),
        str(summary["news_sentiment_state"] or ""),
        str(next(iter(summary["earnings_regime_labels_by_symbol"].values()), "") if summary["earnings_regime_labels_by_symbol"] else ""),
        str(summary["macro_liquidity_state"] or ""),
        str(summary["market_risk_state"] or ""),
        str(next(iter(summary["fundamental_quality_labels_by_symbol"].values()), "") if summary["fundamental_quality_labels_by_symbol"] else ""),
        str(summary["flows_positioning_state"] or ""),
        str(options_regime_label or ""),
    ]
    if all(state for state in states):
        if any("TIGHT" in state for state in states):
            summary["descriptive_market_evidence_state"] = "RISK_OFF_EVIDENCE"
        elif any("EASY" in state for state in states):
            summary["descriptive_market_evidence_state"] = "RISK_ON_EVIDENCE"
        elif any("RISK_OFF" in state for state in states):
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
