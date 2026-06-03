# Volatility Index Source Entitlement Strategy

Purpose:
- document the current entitlement state for the VIX-family live source path
- define the source selection criteria before any writer or persistence approval
- keep the ingestion repo boundary separate from `ai-market-machine-data` and AI Machine

Observed live-source dry run:
- requested symbols: `VIX`, `VVIX`, `VXN`, `RVX`
- fetched count: `0`
- accepted count: `0`
- rejected count: `0`
- warnings:
  - `VIX: unexpected http status: 403`
  - `VVIX: unexpected http status: 403`
  - `VXN: unexpected http status: 403`
  - `RVX: unexpected http status: 403`
- error categories: `vendor_error`
- `no_db_writes=true`
- `no_scheduler_activation=true`
- `no_persistence=true`

What the result proves:
- the dry-run safety gates worked
- no data was written
- the live Polygon path did not return usable observations for the VIX-family symbols under the current entitlement
- the current source path is not validated for production persistence

What remains blocked:
- real writer handoff
- persistence
- scheduler activation
- any downstream consumer enablement that depends on stored volatility observations
- writer remains blocked until a valid source is confirmed

Why writer and persistence remain blocked:
- a source that returns `403` for all four starter symbols cannot be treated as production-ready
- the writer boundary would have no validated upstream data to persist
- the repo must not bypass the source gate just to unlock storage
- source attribution and lineage would be incomplete without a confirmed vendor path

Candidate source options:
1. Polygon entitlement upgrade or plan confirmation
   - keep the current Polygon mapping if the account can be upgraded to permit the VIX-family path
   - re-run the existing dry-run only after entitlement is confirmed
2. Alternate vendor support already present in repo
   - reuse an existing adapter only if it can cover `VIX`, `VVIX`, `VXN`, and `RVX`
   - require stable source attribution, symbol mapping, and lineage metadata
3. FRED/CBOE-style source if appropriate
   - only adopt if the repo already contains the source contract or adapter needed for these symbols
   - do not assume a generic FRED path can replace a volatility-index vendor without explicit coverage
4. Manual seed/backfill file path only if separately approved
   - use only for an explicitly approved, testable backfill or seed flow
   - keep it separate from live entitlement validation and separate from automatic runtime activation

Source selection criteria:
- coverage for `VIX`, `VVIX`, `VXN`, and `RVX`
- historical availability
- daily close availability
- licensing and entitlement clarity
- stable symbol mapping
- lineage and source attribution
- rate-limit behavior
- production reliability

Recommended next step:
- confirm whether the organization wants a Polygon entitlement upgrade decision first or a source-research fallback first
- if an alternate vendor already exists in repo, validate it against the coverage and lineage criteria before any persistence work
- keep writer and persistence blocked until the source is confirmed

Non-goals:
- no DB writes
- no scheduler activation
- no `ai-market-machine-data` changes
- no AI Machine changes
- no live vendor calls in documentation-only work
