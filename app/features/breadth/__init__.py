"""Breadth feature deterministic evidence package.

The canonical implementation now lives in split engine modules and the
`breadth_observation_builder` module. Legacy `breadth_engine` and
`breadth_builder` imports remain as compatibility wrappers.
"""

from app.features.breadth.advance_decline_engine import (
    calculate_advance_decline_line,
    calculate_advance_decline_ratio,
    calculate_advancers_decliners_unchanged,
    calculate_advancing_declining_volume,
)
from app.features.breadth.breadth_observation_builder import build_breadth_observation
from app.features.breadth.highs_lows_engine import calculate_new_highs_lows
from app.features.breadth.moving_average_breadth_engine import calculate_percent_above_100d_ma, calculate_percent_above_moving_average
from app.features.breadth.participation_score_engine import calculate_breadth_score, calculate_participation_score

__all__ = [
    "build_breadth_observation",
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
