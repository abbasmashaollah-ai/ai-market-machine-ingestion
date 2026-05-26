# Manual FMP Daily OHLCV Runner

`scripts/run_fmp_ohlcv_daily_update.py` is the manual FMP daily OHLCV runner in `ai-market-machine-ingestion`.

## Relationship to fan-out

The runner delegates all ingestion work to `app.ingestion.ohlcv.fanout.build_multi_symbol_ohlcv_fanout(...)`.

That means the runner does not duplicate:

- vendor fetch logic
- normalization logic
- write-plan construction
- checkpoint plan construction
- per-symbol error classification

## Scope

The runner:

- accepts repeated `--symbol`
- accepts either `--as-of-date` or an explicit `--start-date` / `--end-date` range
- accepts `--fail-fast`
- accepts `--confirm-write` to enable the approved writer handoff
- accepts `--dry-run` to force writer execution off
- accepts `--record-run` to persist a compact operational summary
- accepts `--record-quality` to persist compact quality rows
- accepts `--record-lineage` to persist compact lineage rows
- accepts `--max-symbols` as a safety cap
- keeps writer execution disabled by default
- prints a deterministic daily-run payload

## Default behavior

Default mode is dry-run/write-plan only.

That means:

- `writer_execution_requested` is false in the underlying fan-out path
- `did_write_db` remains false unless a caller explicitly wires execution in a future staged path
- run history, quality, and lineage persistence stay opt-in through explicit flags

When `--confirm-write` is supplied, the runner enables the existing `OhlcvWriter` handoff and still keeps all writes isolated to the approved writer/stores.

## Writer and checkpoint pass-through

The runner is intentionally conservative.

It does not add scheduler or cron wiring.

Those controls stay explicit at the orchestration layer so the batch runner can be used as a safe replacement candidate for the old data-repo daily FMP job behavior without turning into an automated persistence surface.

## Failure handling

Per-symbol failures from the fan-out layer are treated as non-success.

When `--fail-fast` is enabled, the runner stops after the first failed symbol.

## Evidence chain

`scripts/verify_fmp_ohlcv_evidence_chain.py` is the companion read-only verifier for confirming:

- canonical rows when confirmed-write mode is requested
- run history when `--record-run` is used
- quality rows when `--record-quality` is used
- lineage rows when `--record-lineage` is used

It never writes data and never requires scheduler or API ownership.

## Why scheduler and cron remain disabled

This runner is a manual operator entrypoint only.

Scheduler and cron wiring remain out of scope so the ingestion-side replacement can be verified safely before any automatic daily ownership is reconsidered.

## Why this matters for the data repo

This runner gives `ai-market-machine-ingestion` a manual daily FMP OHLCV orchestration surface built on the existing multi-symbol fan-out contract.

That is the missing ingestion-side replacement candidate for the old data-repo daily FMP ingestion behavior and a prerequisite for eventual data-repo facade or removal work.

The companion verifier lives in `scripts/verify_fmp_ohlcv_evidence_chain.py`, and it shares its PASS/WARN/FAIL semantics with the Polygon verifier through `scripts.evidence_chain_helpers`.
