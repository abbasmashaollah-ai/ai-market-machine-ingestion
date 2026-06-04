# app/features/volatility

This package hosts the deterministic dry-run volatility feature slice.

It builds fixture-only volatility evidence and reports without vendor calls, database writes, or scheduler activation.

## Boundary

- deterministic evidence only
- no DB writes
- no vendor calls in the feature package
- no scheduler activation
- no AI decision, judge, capital, or trading logic

## Current Output Contract

The dry-run observation/report path preserves the legacy fields and also supports backward-compatible aliases and metadata:

- legacy fields
  - `vix_level`
  - `vvix_level`
  - `vxn_level`
  - `rvx_level`
  - `composite_volatility_stress_score`
  - `volatility_regime_label`
- aliases
  - `vix_close`
  - `vvix_close`
  - `vxn_close`
  - `rvx_close`
  - `volatility_stress_score`
  - `descriptive_volatility_state`
- metadata
  - `source_attribution`
  - `dataset_version`
  - `created_at`
  - `updated_at`

The package remains dry-run only and uses stable deterministic timestamps for missing metadata defaults.
