"""Compatibility aggregator for breadth evidence helpers.

This module keeps the legacy import path stable while the implementation is
split into focused engine modules.
"""

from __future__ import annotations

from app.features.breadth.advance_decline_engine import (
    calculate_advance_decline_line,
    calculate_advance_decline_ratio,
    calculate_advancers_decliners_unchanged,
    calculate_advancing_declining_volume,
)
from app.features.breadth.highs_lows_engine import calculate_new_highs_lows
from app.features.breadth.moving_average_breadth_engine import calculate_percent_above_100d_ma, calculate_percent_above_moving_average
from app.features.breadth.participation_score_engine import calculate_breadth_score, calculate_participation_score

__all__ = [
    "calculate_advancers_decliners_unchanged",
    "calculate_advancing_declining_volume",
    "calculate_advance_decline_ratio",
    "calculate_advance_decline_line",
    "calculate_percent_above_moving_average",
    "calculate_percent_above_100d_ma",
    "calculate_new_highs_lows",
    "calculate_breadth_score",
    "calculate_participation_score",
]
