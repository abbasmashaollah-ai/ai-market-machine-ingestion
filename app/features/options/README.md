# options

Dry-run options evidence slice.

This package converts fixture options metrics into deterministic evidence objects and reports.

It is evidence-only:
- no AI decision
- no trading signal
- no vendor calls
- no database writes

## Current Contract

Supported observation/report fields:
- `symbol`
- `underlying_symbol`
- `observation_date`
- `timestamp`
- `expiration_date`
- `implied_volatility_level`
- `realized_vs_implied_score`
- `iv_rank_score`
- `put_call_pressure_score`
- `call_pressure_score`
- `gamma_pressure_score`
- `skew_pressure_score`
- `iv_term_structure_score`
- `options_regime_label`
- `total_volume`
- `total_open_interest`
- `source`
- `source_attribution`
- `quality_status`
- `certification_status`
- `freshness_status`
- `lineage`
- `evidence`
- `dataset_version`
- `created_at`
- `updated_at`
- `no_db_writes`
- `no_vendor_calls`
- `no_scheduler_activation`

## Deferred

Not implemented yet:
- `put_call_volume_ratio`
- `put_call_open_interest_ratio`
- `open_interest_concentration_score`
- `options_volume_anomaly_score`
- `max_pain_price`
- `distance_to_max_pain`
- `gamma_exposure_estimate`
- `delta_exposure_estimate`
- `dealer_positioning_proxy`
- `options_stress_score`
- `descriptive_options_state`
- live vendor options-chain fetching
- DB writes
- scheduler activation
- AI Machine, judge, capital, or trading decisions
