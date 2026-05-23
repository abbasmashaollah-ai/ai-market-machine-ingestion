# US Market Calendar Helper

`app/market_calendar/us_market_calendar.py` provides a small dependency-free helper for OHLCV coverage and gap diagnostics.

## Scope

The helper currently:

- generates expected trading days between `start_date` and `end_date`
- uses exclusive end-date semantics through the calling code
- excludes weekends
- excludes a small explicit known-closure set

Current known closures:

- `2025-01-09`

## Limitation

This is not a complete exchange calendar. It is a minimal helper for manual diagnostic and repair workflows, and additional closures must be added explicitly.

For readiness diagnostics and the future expansion path, see [US Market Calendar Readiness](us_market_calendar_readiness.md).
