# Polygon OHLCV Scheduler Design

This document defines the intended architecture guardrails for future Polygon OHLCV daily automation.

It is design-only. There is no scheduler implementation in this repository yet.

The repository now also contains a disabled-by-default scheduler stub at `scripts/run_polygon_ohlcv_scheduler_cycle.py`. It remains inert unless the explicit enable flag and environment variable are both set.
The disabled-state verifier `scripts.verify_polygon_scheduler_disabled.py` confirms that the scheduler stays off by default and does not become active on Railway startup without an explicit opt-in.

## Current Manual Readiness State

The repository already has the manual building blocks needed for safe future automation:

- daily planner: `scripts/plan_polygon_ohlcv_daily_update.py`
- daily runner: `scripts/run_polygon_ohlcv_daily_update.py`
- scheduler-readiness planner: `scripts/plan_polygon_ohlcv_scheduler_cycle.py`
- evidence-chain verification: `scripts/verify_polygon_ohlcv_evidence_chain.py`
- run, quality, and lineage recording through approved operational stores

These tools are manual and read-only where documented. They are operator-run diagnostics, not automation.

## Future Scheduler Principles

Any future scheduler must follow these constraints:

- disabled by default
- never run on Railway startup unless explicitly enabled
- require an explicit environment flag to activate
- enforce request budgets before execution
- enforce rate-limit controls before and during execution
- write operational run history, quality results, and lineage through the approved stores when enabled
- fail safely without leaking secrets
- use this ingestion repository for vendor fetching and normalization orchestration
- not move schema ownership into ingestion

Schema ownership remains with `ai-market-machine-data`.

## Proposed Scheduler Flow

The intended future flow is:

1. Plan the cycle.
2. Check the request budget.
3. Execute the daily runner for symbols that need an update.
4. Record run history, quality, and lineage when enabled and supported.
5. Verify the evidence chain after the run.
6. Emit a compact operator summary.

This flow preserves the current manual contracts and adds automation only as a later, explicit step.

## Hard Blockers Before Enablement

The scheduler must not be enabled until these are in place:

- complete market calendar coverage
- symbol universe governance
- quota policy
- alerting and monitoring
- production Railway environment review
- vendor tier review

Without those controls, automation would be operationally fragile.

## Polygon Flat-File Note

The Polygon API remains the live/recent path for incremental updates and gap fills.

Polygon flat files should be added later as a historical backfill source adapter.

Both sources must feed the same normalization, validation, writer, and evidence pipeline.

That keeps the canonical output contract stable while allowing source diversity later.
