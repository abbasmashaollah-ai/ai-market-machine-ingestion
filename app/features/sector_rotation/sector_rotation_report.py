"""JSON-friendly report helpers for sector rotation dry-run results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.features.sector_rotation.sector_rotation_job import SectorRotationDryRunResult


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _normalize_symbol(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().upper()


def _numeric_value(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def summarize_sector_observations(
    observation_rows: Sequence[Mapping[str, object]],
    top_n: int = 3,
) -> dict[str, object]:
    """Summarize sector observation rows into a compact JSON-friendly payload."""

    ranked = []
    for row in observation_rows:
        symbol = _normalize_symbol(row.get("sector_symbol"))
        if not symbol:
            continue
        momentum = _numeric_value(row.get("momentum_score"))
        rank_20d = _numeric_value(row.get("rank_20d"))
        score = momentum if momentum is not None else (-(rank_20d or 0.0))
        ranked.append(
            {
                "sector_symbol": symbol,
                "momentum_score": momentum,
                "rank_20d": rank_20d,
                "leadership_flag": bool(row.get("leadership_flag", False)),
                "deterioration_flag": bool(row.get("deterioration_flag", False)),
                "is_defensive_sector": bool(row.get("is_defensive_sector", False)),
                "is_cyclical_sector": bool(row.get("is_cyclical_sector", False)),
                "is_growth_sector": bool(row.get("is_growth_sector", False)),
                "is_rate_sensitive_sector": bool(row.get("is_rate_sensitive_sector", False)),
                "_score": score,
            }
        )

    ranked.sort(key=lambda item: (-float(item["_score"]), item["sector_symbol"]))
    strongest = [item["sector_symbol"] for item in ranked[: max(1, int(top_n))]]
    weakest = [item["sector_symbol"] for item in list(reversed(ranked))[: max(1, int(top_n))]]
    leadership_sectors = [item["sector_symbol"] for item in ranked if item["leadership_flag"]]
    deteriorating_sectors = [item["sector_symbol"] for item in ranked if item["deterioration_flag"]]
    defensive_represented = [item["sector_symbol"] for item in ranked if item["is_defensive_sector"]]
    cyclical_represented = [item["sector_symbol"] for item in ranked if item["is_cyclical_sector"]]
    growth_represented = [item["sector_symbol"] for item in ranked if item["is_growth_sector"]]
    rate_sensitive_represented = [item["sector_symbol"] for item in ranked if item["is_rate_sensitive_sector"]]

    return {
        "strongest_sectors": strongest,
        "weakest_sectors": weakest,
        "leadership_sectors": leadership_sectors,
        "deteriorating_sectors": deteriorating_sectors,
        "defensive_represented": defensive_represented,
        "cyclical_represented": cyclical_represented,
        "growth_represented": growth_represented,
        "rate_sensitive_represented": rate_sensitive_represented,
    }


def build_sector_rotation_dry_run_report(dry_run_result: SectorRotationDryRunResult) -> dict[str, object]:
    """Build a compact JSON-friendly inspection report from a dry-run result."""

    core_result = dry_run_result.dry_run_result or dry_run_result
    observation_rows = tuple(getattr(core_result, "observation_rows", ()))
    summary_row = dict(getattr(core_result, "summary_row", {}))
    accepted_observation_count = getattr(core_result, "accepted_observation_count", getattr(dry_run_result, "accepted_observation_count", 0))
    accepted_summary_count = getattr(core_result, "accepted_summary_count", getattr(dry_run_result, "accepted_summary_count", 0))
    rejected_observation_count = getattr(core_result, "rejected_observation_count", getattr(dry_run_result, "rejected_observation_count", 0))
    rejected_summary_count = getattr(core_result, "rejected_summary_count", getattr(dry_run_result, "rejected_summary_count", 0))
    sector_summary = summarize_sector_observations(observation_rows)

    return {
        "universe": summary_row.get("universe"),
        "observation_date": summary_row.get("observation_date"),
        "descriptive_rotation_state": summary_row.get("descriptive_rotation_state"),
        "top_sector_symbols": _as_list(summary_row.get("top_sector_symbols")),
        "bottom_sector_symbols": _as_list(summary_row.get("bottom_sector_symbols")),
        "risk_on_leadership_score": summary_row.get("risk_on_leadership_score"),
        "cyclical_leadership_score": summary_row.get("cyclical_leadership_score"),
        "defensive_leadership_score": summary_row.get("defensive_leadership_score"),
        "leadership_concentration_score": summary_row.get("leadership_concentration_score"),
        "sector_dispersion_score": summary_row.get("sector_dispersion_score"),
        "broad_rotation_flag": summary_row.get("broad_rotation_flag"),
        "narrow_rotation_flag": summary_row.get("narrow_rotation_flag"),
        "improving_rotation_flag": summary_row.get("improving_rotation_flag"),
        "deteriorating_rotation_flag": summary_row.get("deteriorating_rotation_flag"),
        "observation_count": len(observation_rows),
        "accepted_observation_count": accepted_observation_count,
        "accepted_summary_count": accepted_summary_count,
        "rejected_observation_count": rejected_observation_count,
        "rejected_summary_count": rejected_summary_count,
        "warnings": list(getattr(dry_run_result, "warnings", ())),
        "no_db_writes": getattr(dry_run_result, "no_db_writes", True),
        "no_vendor_calls": getattr(dry_run_result, "no_vendor_calls", True),
        "no_scheduler_activation": getattr(dry_run_result, "no_scheduler_activation", True),
        "observation_summary": sector_summary,
        "observations": [dict(row) for row in observation_rows],
    }
