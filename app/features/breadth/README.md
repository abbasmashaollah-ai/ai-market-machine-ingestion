# breadth

Deterministic breadth and participation evidence helpers for dry-run use only.

This package builds breadth observations from fixture OHLCV histories, validates them, writes them to an in-memory mock writer, and produces JSON-friendly dry-run reports. Real writer and persistence behavior remains deferred.

Current dry-run breadth evidence includes current-period net breadth for `advance_decline_line`; it is not a persisted cumulative advance/decline line.

## Module Layout

Active modules:
- `advance_decline_engine.py`
- `highs_lows_engine.py`
- `moving_average_breadth_engine.py`
- `participation_score_engine.py`
- `breadth_observation_builder.py`
- `breadth_writer.py`
- `breadth_job.py`

Compatibility wrappers:
- `breadth_engine.py`
- `breadth_builder.py`

Deferred modules:
- `equal_weight_divergence_engine.py`
- `breadth_thrust_engine.py`
- `sector_participation_engine.py`

Notes:
- `advance_decline_engine` is active.
- `highs_lows_engine` is active for current breadth evidence.
- `moving_average_breadth_engine` is active.
- `participation_score_engine` is active.
- `breadth_observation_builder` is the canonical builder.
- `breadth_builder` is compatibility-only.
- 52-week high/low evidence remains deferred until the historical window and universe contract are explicit.
- breadth remains deterministic evidence only; no final regime, judge posture, capital permission, or trade signal logic is implemented here.
