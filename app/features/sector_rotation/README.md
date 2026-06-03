# Sector Rotation

This package is the first deterministic evidence vertical slice under `app/features/`.

It exists to calculate sector rotation evidence from a fixed ETF universe without introducing vendor access, persistence, or AI decision logic.

The sector universe definitions, return calculations, and relative-strength calculations now exist. The certified OHLCV row-to-history transformer, live single-symbol read adapter, mock writer handoff, and dry-run orchestration job now exist as well. Writer behavior, persistence, job orchestration, and scheduler activation are still deferred.
The sector leadership ranking, leadership flag, deterioration flag, and momentum score helper now also exist. Defensive, cyclical, and risk-on grouping scores now exist as well. Sector dispersion, daily summary evidence, warehouse-shaped observation builders, deterministic validators, a mock writer handoff, and a dry-run orchestration job now exist too. The dry-run vertical slice is complete in memory and proves the full feature flow without persistence. Writer behavior, persistence, job orchestration, and scheduler activation are still deferred.

## Purpose

Sector rotation is a narrow, deterministic market evidence slice. It should compute relative performance and leadership evidence for the SPDR sector ETF universe and hand that evidence off to the warehouse boundary later.

## First Vertical Slice Rationale

This is the recommended first feature slice because it is:

- deterministic
- narrow enough to keep the boundary clean
- aligned to existing `sector_rotation_observations` and `sector_rotation_daily_summary` tables in the data repo
- based on a fixed universe instead of an open-ended source expansion problem

## Sector ETF Universe

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

## Target Data Repo Tables

- `sector_rotation_observations`
- `sector_rotation_daily_summary`

## Target Output Fields

- `return_1d`
- `return_5d`
- `return_20d`
- `return_60d`
- `relative_strength_5d_vs_spy`
- `relative_strength_20d_vs_spy`
- `relative_strength_60d_vs_spy`
- `rank_5d`
- `rank_20d`
- `rank_60d`
- `rank_change_5d`
- `rank_change_20d`
- `momentum_score`
- `leadership_flag`
- `deterioration_flag`
- `risk_on_leadership_score`
- `defensive_leadership_score`
- `leadership_concentration_score`
- `sector_dispersion_score`
- `broad_rotation_flag`
- `narrow_rotation_flag`
- `improving_rotation_flag`
- `deteriorating_rotation_flag`

## Planned Implementation Stages

1. sector universe + dataclasses
2. returns and relative strength pure engines
3. rank and leadership pure engines
4. defensive/cyclical grouping engines
5. daily summary engine
6. observation builders
7. validators
8. mock writer handoff
9. real writer/persistence only after approval
10. job/orchestration only after dry-run proof
11. scheduler activation last

## Explicit Non-Goals

- no vendor calls
- no DB writes
- no scheduler activation
- no AI regime logic
- no judge posture
- no trading logic
- no capital logic
- no portfolio logic
- no AI confidence logic

Current implementation status:

- sector universe implementation exists
- pure return engine exists
- pure relative-strength engine exists
- leadership ranking and momentum helpers exist
- defensive/cyclical/risk-on grouping helpers exist
- dispersion and daily summary helpers exist
- warehouse-shaped observation builders exist
- payload validators exist
- mock writer handoff exists
- dry-run orchestration job exists
- writer/persistence/job/scheduler stages are not implemented yet

Group scores, descriptive summary states, observation payloads, validators, and mock writer handoff are deterministic evidence only. They are not final AI regime decisions, judge posture, trading signals, capital allocation, or portfolio logic.

The dry-run job uses in-memory price histories, proves the full feature flow through the mock writer, and does not touch the database. Real persistence requires separate approval.

The dry-run vertical slice is a completion checkpoint, not a production persistence contract. Real writer implementation remains separate work.

The next planning step is the certified OHLCV reader contract, which should shape approved OHLCV rows into the existing `price_history_by_symbol` dry-run input without changing the feature pipeline.

The pure row-to-history transformer now exists. The API/client reader adapter is still not implemented.

The adapter review is documented separately and currently blocks runtime adapter implementation until an approved data-read client contract exists.

The live verification plan for the client and adapter is documented, but no live read has been executed.

The live route has since been confirmed as single-symbol; the adapter calls the client once per required symbol and combines `historical_ohlcv` rows before the dry-run pipeline.
Live warehouse coverage for the 11 sector ETFs is currently missing, so production sector rotation remains blocked until certified OHLCV is populated for that universe.
