# Price Feature Checkpoint

## Completed In `app/features/prices`

The price dry-run package now supports both close-only and OHLCV-style inputs.

Current deterministic outputs include:
- returns
- moving averages
- distance from moving averages
- ATR
- dollar volume
- average dollar volume
- relative volume
- liquidity score
- trend state evidence

The package remains a dry-run evidence builder, validator, mock writer, and report layer.

## Updated In `app/features/market_features/fixtures/price_fixtures.py`

`build_price_ohlcv_fixtures()` now returns deterministic OHLCV rows for:
- `SPY`
- `AAPL`
- `MSFT`

Each row includes:
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

The fixture file only generates input data. It does not calculate price features.

## Why We Stopped Here

This step aligns the bundle fixture with the finalized price dry-run package and exercises the OHLCV path without widening the scope into persistence, live ingestion, or downstream interpretation.

## Deferred Work

Deferred items remain intentionally out of scope:
- forward returns are research/replay-only because of lookahead risk
- beta requires aligned benchmark history
- correlation requires aligned multi-symbol or benchmark histories
- idiosyncratic strength requires benchmark-relative logic
- real reader/writer persistence waits for an approved data-side contract

## Boundary Confirmation

This change preserves the dry-run boundary:
- no DB writes
- no vendor calls
- no live API calls
- no scheduler activation
- no data repo changes
- no AI Machine changes
