# app/features

`app/features/` is the deterministic evidence layer for `ai-market-machine-ingestion`.

This package is for feature calculation only. It is where ingestion turns approved, normalized market data into deterministic evidence objects that can later be handed off to the warehouse layer.

## Scope

What belongs here:

- deterministic evidence calculations
- feature observation assembly
- feature-domain validation helpers
- feature-domain read helpers
- feature-domain orchestration jobs
- domain-specific evidence packaging for writer handoff

What does not belong here:

- vendor calls
- raw payload fetching
- source planning
- raw-to-canonical normalization
- database writes
- scheduler activation
- AI regime logic
- judge logic
- buy/sell logic
- capital allocation
- portfolio logic
- AI confidence logic

## Standard Domain Pattern

Each feature domain should follow the same pattern:

`reader -> engine/calculator -> observation_builder -> validator -> writer -> job`

The module naming can vary by domain, but the responsibility split should not.

## Boundary With Other Packages

- `app/vendors/` stays on vendor clients and adapters
- `app/sources/` stays on source planning and availability
- `app/normalization/` stays on raw-to-canonical shaping
- `app/writers/` stays on approved persistence and writer handoff
- `app/quality/` stays on validation and certification support
- `app/state/` stays on checkpoints, run state, lineage, and quality persistence

Feature calculators must not call vendors directly and must not write to the database.

## Planned Domains

- `prices`
- `universe`
- `breadth`
- `sector_rotation`
- `volatility`
- `options`
- `macro_liquidity`
- `flows_positioning`
- `fundamentals`
- `earnings`
- `news_sentiment`
- `event_calendar`
- `cross_asset`

## Started Domains

- `prices` dry-run feature slice
- `breadth` dry-run feature slice
- `market_features` aggregate dry-run bundle layer for `prices`, `breadth`, `sector_rotation`, `cross_asset`, and `liquidity_rates`
- `volatility` dry-run feature slice
- `event_calendar` dry-run feature slice
- `news_sentiment` dry-run feature slice
- `fundamentals` dry-run feature slice

## Local Dry-Run Artifacts

- Bundle and summary exports can be written under `outputs/dry_runs/` for local inspection only.
