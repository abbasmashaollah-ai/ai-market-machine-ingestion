# Event Calendar Readiness Summary

This summary records the current event-calendar readiness state in `ai-market-machine-ingestion`.
It is documentation only.

## Current State

- The canonical event-calendar contract exists in `ai-market-machine-data`.
- The dry-run foundation exists.
- The source plan exists.
- The preflight exists.
- The evidence plan exists.
- The writer plan exists, but persistence remains deferred.
- The OPEX deterministic slice is verified.
- The CPI/FOMC/NFP macro-event fixture foundation exists.
- The macro-event source plan exists.
- Live BLS and Federal Reserve adapters are not built yet.
- No DB writes are enabled.
- The earnings calendar plan exists as the next event-calendar subdomain.

## Next Options

- BLS live dry-run
- Federal Reserve FOMC dry-run
- earnings calendar plan
- earnings calendar vertical slice planning

## Boundary

No vendor calls are made by this summary.
No DB writes are enabled.
No scheduler, FastAPI route, migration, schema ownership, AI, trading, risk, signal, regime, or portfolio logic belongs here.
