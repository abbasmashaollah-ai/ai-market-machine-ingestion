# US Market Calendar Readiness

`scripts.diagnose_us_market_calendar_readiness` is a read-only diagnostic for the current US market calendar helper.

## Current state

The calendar helper is intentionally minimal:

- it excludes weekends
- it excludes a small explicit known-closure set
- it is deterministic and dependency-free

Current known closure:

- `2025-01-09`

## Limitations

The helper is not production complete. Before scheduler enablement or large-scale historical backfills, the calendar layer should be expanded to cover:

- full holiday calendar support
- special market closures
- early close schedules
- a durable exchange schedule source

The future replacement should remain deterministic and testable, and Polygon flat-file historical ingestion should use the same calendar expectations for coverage validation.

The production target is documented in [Market Calendar Production Upgrade](market_calendar_production_upgrade.md). The current helper remains safe for manual tests only.

`ai-market-machine-data` remains the schema owner.
