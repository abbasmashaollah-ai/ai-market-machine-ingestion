# ETF/Index Universe Expansion Plan

## Purpose

Expand the symbol-master universe from core liquid ETFs and major indexes into a broader ETF/index coverage set.

## Dependency

This plan depends on the symbol_master foundation already being established and verified.

## Target groups

- SPY
- QQQ
- IWM
- DIA
- sector ETFs
- industry ETFs
- major indexes

## Contract dependency

This work depends on the data repo symbol_master contract and the approved manual ingestion boundaries.

## Ingestion responsibilities

- keep vendor fetching separate from normalization
- keep persistence inside the approved writer/store boundaries
- keep coverage verification read-only
- keep expansion staged in small batches

## Boundary

- no scheduler yet
- no AI/trading logic
- no FastAPI routes
- no migrations
- no schema ownership
- no vendor calls outside the approved manual path

## Planned operator pattern

- preflight
- runner
- evidence verification
- coverage assessment

The exact commands should mirror the symbol-master manual workflow before any broader expansion is attempted.
