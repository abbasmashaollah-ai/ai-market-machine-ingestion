"""Sector rotation daily summary and descriptive evidence state helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.features.sector_rotation.cyclical_rotation_engine import calculate_risk_on_leadership_score
from app.features.sector_rotation.defensive_rotation_engine import calculate_defensive_leadership_score
from app.features.sector_rotation.sector_dispersion_engine import (
    calculate_leadership_concentration_score,
    calculate_sector_dispersion_score,
    detect_broad_rotation,
    detect_narrow_rotation,
)
from app.features.sector_rotation.sector_leadership_engine import build_sector_leadership_snapshot, is_deteriorating


def get_top_bottom_symbols(values_by_symbol: Mapping[str, float | int | None], top_n: int = 3) -> tuple[list[str], list[str]]:
    """Return deterministic top and bottom symbol lists."""

    valid = []
    for symbol, value in values_by_symbol.items():
        if value is None:
            continue
        try:
            valid.append((symbol.strip().upper(), float(value)))
        except (AttributeError, TypeError, ValueError):
            continue
    if not valid:
        return ([], [])
    valid.sort(key=lambda item: item[0])
    ranked_desc = sorted(valid, key=lambda item: (-item[1], item[0]))
    ranked_asc = sorted(valid, key=lambda item: (item[1], item[0]))
    count = max(1, min(int(top_n), len(valid)))
    return ([symbol for symbol, _ in ranked_desc[:count]], [symbol for symbol, _ in ranked_asc[:count]])


def detect_improving_rotation(leadership_snapshot: Mapping[str, Mapping[str, float | int | bool | None]] | None) -> bool:
    """Return True when at least one leader is improving and not deteriorating."""

    if not leadership_snapshot:
        return False
    for snapshot in leadership_snapshot.values():
        rank_change_5d = snapshot.get("rank_change_5d")
        rank_change_20d = snapshot.get("rank_change_20d")
        if any(change is not None and change > 0 for change in (rank_change_5d, rank_change_20d)):
            if not snapshot.get("deterioration_flag", False):
                return True
    return False


def detect_deteriorating_rotation(leadership_snapshot: Mapping[str, Mapping[str, float | int | bool | None]] | None) -> bool:
    """Return True when the leadership snapshot shows weakening evidence."""

    if not leadership_snapshot:
        return False
    return any(bool(snapshot.get("deterioration_flag", False)) for snapshot in leadership_snapshot.values())


def determine_descriptive_rotation_state(
    risk_on_leadership_score: float | int | None = None,
    defensive_leadership_score: float | int | None = None,
    broad_rotation_flag: bool = False,
    narrow_rotation_flag: bool = False,
    deteriorating_rotation_flag: bool = False,
) -> str:
    """Return a descriptive evidence label only.

    This is not a final market regime, judge posture, or trading decision.
    """

    if deteriorating_rotation_flag:
        if narrow_rotation_flag:
            return "BROAD_DETERIORATION"
        return "MIXED_ROTATION"

    if risk_on_leadership_score is not None and defensive_leadership_score is not None:
        try:
            risk_on = float(risk_on_leadership_score)
            defensive = float(defensive_leadership_score)
        except (TypeError, ValueError):
            risk_on = defensive = 0.0
        if risk_on > defensive and broad_rotation_flag:
            return "RISK_ON_LEADERSHIP"
        if defensive > risk_on and narrow_rotation_flag:
            return "DEFENSIVE_LEADERSHIP"
        if broad_rotation_flag:
            return "BROAD_IMPROVEMENT"
        if narrow_rotation_flag:
            return "NARROW_LEADERSHIP"

    if broad_rotation_flag and narrow_rotation_flag:
        return "MIXED_ROTATION"
    if broad_rotation_flag:
        return "BROAD_IMPROVEMENT"
    if narrow_rotation_flag:
        return "NARROW_LEADERSHIP"
    return "NO_CLEAR_ROTATION"


def build_sector_rotation_daily_summary(
    symbol_scores: Mapping[str, float | int | None],
    leadership_snapshot: Mapping[str, Mapping[str, float | int | bool | None]] | None = None,
) -> dict[str, object]:
    """Build the daily sector rotation evidence summary."""

    top_sector_symbols, bottom_sector_symbols = get_top_bottom_symbols(symbol_scores, top_n=3)
    leadership_snapshot = leadership_snapshot or build_sector_leadership_snapshot({"5d": symbol_scores})

    risk_on_leadership_score = calculate_risk_on_leadership_score(symbol_scores)
    defensive_leadership_score = calculate_defensive_leadership_score(symbol_scores)
    sector_dispersion_score = calculate_sector_dispersion_score(symbol_scores)
    leadership_concentration_score = calculate_leadership_concentration_score(symbol_scores, top_n=3)
    broad_rotation_flag = detect_broad_rotation(symbol_scores)
    narrow_rotation_flag = detect_narrow_rotation(symbol_scores)
    improving_rotation_flag = detect_improving_rotation(leadership_snapshot)
    deteriorating_rotation_flag = detect_deteriorating_rotation(leadership_snapshot)

    return {
        "risk_on_leadership_score": risk_on_leadership_score,
        "defensive_leadership_score": defensive_leadership_score,
        "leadership_concentration_score": leadership_concentration_score,
        "sector_dispersion_score": sector_dispersion_score,
        "broad_rotation_flag": broad_rotation_flag,
        "narrow_rotation_flag": narrow_rotation_flag,
        "improving_rotation_flag": improving_rotation_flag,
        "deteriorating_rotation_flag": deteriorating_rotation_flag,
        "top_sector_symbols": top_sector_symbols,
        "bottom_sector_symbols": bottom_sector_symbols,
        "descriptive_rotation_state": determine_descriptive_rotation_state(
            risk_on_leadership_score=risk_on_leadership_score,
            defensive_leadership_score=defensive_leadership_score,
            broad_rotation_flag=broad_rotation_flag,
            narrow_rotation_flag=narrow_rotation_flag,
            deteriorating_rotation_flag=deteriorating_rotation_flag,
        ),
    }
