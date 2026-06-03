# Sector Rotation Live Coverage Blocker

## Purpose

This document records the live coverage blocker for `sector_rotation` in `ai-market-machine-ingestion`.

The live read route works, but the warehouse coverage required for production sector rotation is missing for the 11 sector ETFs.

## Live Route Used

- `GET /internal/read/symbol/{symbol}/ohlcv/history`

## Manual Read-Only Verification Result

The following live coverage check was run in read-only mode:

- `SPY`
- `XLC`
- `XLY`
- `XLP`
- `XLE`
- `XLF`
- `XLV`
- `XLI`
- `XLB`
- `XLRE`
- `XLK`
- `XLU`

Observed output:

```text
SPY rows=65 coverage=COMPLETE quality=PASS certification=CERTIFIED
XLC rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLY rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLP rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLE rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLF rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLV rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLI rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLB rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLRE rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLK rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
XLU rows=0 coverage=MISSING quality=WARN certification=UNCERTIFIED
```

## Exact Coverage Table

| Symbol | Rows | Coverage | Quality | Certification |
| --- | ---: | --- | --- | --- |
| SPY | 65 | COMPLETE | PASS | CERTIFIED |
| XLC | 0 | MISSING | WARN | UNCERTIFIED |
| XLY | 0 | MISSING | WARN | UNCERTIFIED |
| XLP | 0 | MISSING | WARN | UNCERTIFIED |
| XLE | 0 | MISSING | WARN | UNCERTIFIED |
| XLF | 0 | MISSING | WARN | UNCERTIFIED |
| XLV | 0 | MISSING | WARN | UNCERTIFIED |
| XLI | 0 | MISSING | WARN | UNCERTIFIED |
| XLB | 0 | MISSING | WARN | UNCERTIFIED |
| XLRE | 0 | MISSING | WARN | UNCERTIFIED |
| XLK | 0 | MISSING | WARN | UNCERTIFIED |
| XLU | 0 | MISSING | WARN | UNCERTIFIED |

## Impact

The sector rotation feature pipeline is ready, but live production sector rotation cannot proceed because certified OHLCV warehouse coverage is missing for the sector ETFs.

As a result:

- the live sector rotation adapter cannot yet produce a valid production dry-run from live warehouse coverage
- real writer/persistence remains blocked
- scheduler activation remains blocked

## What Remains Safe

- in-memory dry-run
- mocked `DataReadClient` tests
- certified OHLCV row-to-history transformer
- sector rotation adapter tests

## Recommended Next Path

Populate certified OHLCV for the 11 sector ETFs in the warehouse before sector writer work.
The next step is to populate certified OHLCV for the missing sector universe coverage before any writer work starts.

Possible follow-up paths:

1. use the existing OHLCV ingestion/backfill pipeline to populate the sector ETFs
2. create a sector ETF OHLCV backfill plan if no existing backfill path is approved
3. verify `symbol_master` entries for the 11 sector ETFs
4. rerun the live coverage check after population

The vendor-deferred development plan is documented in `docs/vendor_deferred_sector_rotation_development_plan.md`.

## Explicit Non-Goals

- no runtime code change
- no DB writes in this step
- no vendor calls in this step
- no scheduler activation
- no AI Machine changes
