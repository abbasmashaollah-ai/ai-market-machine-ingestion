# Market Calendar Mock Provider

This document defines the deterministic fixture provider used by tests.

## Behavior

- `is_trading_day`
- `previous_trading_day`
- `next_trading_day`
- `trading_days`
- `market_open_close`
- `is_early_close`
- `closure_reason`

## Fixture details

- explicit closure: `2025-01-01`
- explicit closure: `2025-01-09`
- early close fixture: `2025-07-03`
- timezone label: `America/New_York`

## Safety

This mock provider does not:

- call external services
- write to the database
- enable production behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
