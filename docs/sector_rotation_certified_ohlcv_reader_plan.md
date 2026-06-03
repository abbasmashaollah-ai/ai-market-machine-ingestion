# Sector Rotation Certified OHLCV Reader Plan

## Purpose

This plan defines the reader layer that will feed the `sector_rotation` dry-run pipeline from certified OHLCV data without changing the deterministic calculation pipeline.

The reader is a source-shaping layer only. It is intended to bridge certified OHLCV rows into the in-memory `price_history_by_symbol` shape already used by the dry-run vertical slice.

## Current Dry-Run Input Shape

The existing dry-run job accepts:

```python
price_history_by_symbol = {
  "SPY": [100, 101, ...],
  "XLK": [50, 51, ...],
}
```

The reader should populate that shape from certified OHLCV rows while preserving the existing calculation flow.

The live single-symbol route now feeds this transformer through the sector rotation adapter.

## Target Certified OHLCV Input Source

The future reader should consume certified OHLCV rows from the approved ingestion/data boundary, not from vendor APIs.

Required symbols:

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

## Expected OHLCV Fields

The reader should expect, at minimum:

- symbol
- date or timestamp
- close
- quality status, if available
- certification status, if available
- freshness status, if available
- source attribution or lineage, if available

The reader should keep only what is needed to construct close histories and minimal evidence metadata for the dry-run path.

## Proposed Reader Responsibility

The sector rotation reader should:

- read certified OHLCV rows
- filter the required symbols
- sort by date
- extract close histories
- return `price_history_by_symbol`
- emit warnings for missing symbols
- emit warnings for insufficient history
- respect quality and certification gates before producing the history map

The live certified OHLCV response shape now confirmed by manual verification includes `historical_ohlcv` rows per symbol, which the adapter combines before calling this transformer.

The reader should not:

- no vendor calls
- no DB writes
- no feature calculations beyond shaping close histories
- no AI interpretation
- no real writer
- no scheduler activation

## Integration Point

The reader will feed the existing dry-run orchestration point:

```python
run_sector_rotation_dry_run(price_history_by_symbol=...)
```

That preserves the existing deterministic feature pipeline and keeps the reader boundary narrow.

## Data-Quality Gate

The reader should reject or warn when:

- certification is missing or not acceptable
- freshness is missing or not acceptable
- a required symbol is missing
- the lookback window is insufficient for the requested return windows

This gate must stay source-side. It should not change the feature calculations.

## Open Questions

- What is the exact internal read endpoint or client for certified OHLCV?
- What auth or token handling is required for that client?
- What lookback window is required to reliably support 60d returns?
- Should the reader use adjusted close or plain close?
- Does the data repo return enough history for all required symbols in one call?

## Recommended Implementation Sequence

1. docs/contract
2. pure row-to-history transformer
3. fake certified OHLCV fixtures
4. reader adapter using the existing client if available
5. dry-run integration with reader output
6. no real writer until approved

The pure row-to-history transformer is now implemented. The API/client reader adapter is still not implemented.

## Approval Gates

Before any runtime reader implementation is enabled, confirm:

- the certified OHLCV read contract
- the exact source-owned client path
- the quality/certification/freshness acceptance rules
- the symbol coverage and lookback requirements
- the writer boundary remains separate

## Non-Goals

This planning step does not include:

- runtime code
- real writer behavior
- DB writes
- vendor calls
- scheduler activation
- `ai-market-machine-data` changes
- `AI Machine` changes

The real writer and persistence path remain blocked until the reader and write contract are approved.

Current implementation status:

- pure row-to-history transformer exists
- fake certified OHLCV fixture coverage exists
- API/client reader adapter is still pending
- dry-run integration can already consume the transformed history map

The runtime adapter review is documented in `docs/sector_rotation_certified_ohlcv_adapter_review.md`. That review currently blocks runtime adapter work until an approved data-read client contract exists.

The shared data-read client contract is documented in `docs/data_read_client_contract.md`.

The mocked `DataReadClient` implementation exists, but live endpoint verification is still pending and the sector rotation runtime adapter remains blocked until that boundary is confirmed.

The sector rotation certified OHLCV adapter now exists as mocked/test-only code and still requires live endpoint verification before any runtime enablement.

The live read plan is documented in `docs/sector_rotation_certified_ohlcv_live_read_plan.md`.

The live route is confirmed as `GET /internal/read/symbol/{symbol}/ohlcv/history`, and the adapter combines single-symbol `historical_ohlcv` rows before feeding the dry-run pipeline.

The live coverage blocker is documented in `docs/sector_rotation_live_coverage_blocker.md`; the 11 sector ETFs are still missing certified warehouse coverage.
