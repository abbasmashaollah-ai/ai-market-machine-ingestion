# Market Feature Bundle Fixture Mode Checkpoint

This checkpoint records the current fixture-mode market evidence bundle milestone.

## Raw and domain evidence sections

- prices
- breadth
- sector_rotation
- cross_asset
- liquidity_rates
- volatility
- event_calendar
- news_sentiment
- fundamentals
- flows_positioning
- options
- earnings

## Synthesized evidence sections

- macro_liquidity
- market_risk
- market_regime

## Synthesizer order

1. Build the raw/domain bundle.
2. Build the compact summary from the raw/domain bundle.
3. Run `macro_liquidity` and append it.
4. Build a summary with `macro_liquidity` available.
5. Run `market_risk` and append it.
6. Build a summary with `macro_liquidity` and `market_risk` available.
7. Run `market_regime` and append it.

## Current health guarantees

- `total_warnings == 0`
- safety flags are true
- rejected counts are zero
- CLI summary-only output works
- validator passes

## Explicit non-goals

- no DB writes
- no vendor calls
- no live API calls
- no LLM calls
- no scheduler activation
- no AI Machine changes

## Next possible stages

- app-owned real data readers
- controlled writer handoff
- warehouse contract alignment
- producer-to-data-repo persistence after approval
- AI Machine consumption last

