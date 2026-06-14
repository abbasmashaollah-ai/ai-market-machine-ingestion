# Production Activation Readiness Update

## Executive Verdict

`NOT_READY_FOR_PRODUCTION_ACTIVATION`

The repository is close on guardrails and contract discipline, but it is not yet ready to be treated as production-active for real OHLCV ingestion. The main reason is that the codebase still mixes production-like persistence primitives with planning-only and dry-run-oriented orchestration, and the safest first real activation candidate is still limited to a controlled single-symbol probe after verification.

## Current Implemented Capabilities

- Vendor fetch capability exists for FMP through a live HTTP client wrapper with retry classification in `app/vendors/fmp/client.py`.
- Polygon vendor transport exists in `app/vendors/polygon/client.py`, including HTTP request building and response extraction.
- OHLCV normalization exists in `app/normalization/ohlcv.py` and produces UTC-normalized `NormalizedOHLCVRecord` objects from raw payloads.
- The normalized OHLCV model enforces UTC timestamps and non-empty timeframe fields in `app/models/normalized.py`.
- The OHLCV writer exists in `app/writers/ohlcv_writer.py` and performs schema checks, uniqueness checks, deduplication, and transactional upserts.
- Run history persistence exists in `app/state/ingestion_run_store.py`.
- Lineage persistence exists in `app/state/data_lineage_store.py`.
- Quality result persistence exists in `app/state/data_quality_result_store.py`.
- Manual checkpoint storage exists in `app/state/manual_polygon_ohlcv_checkpoint_store.py`.
- Manual Polygon incremental OHLCV support exists in `app/ingestion/manual/polygon_ohlcv_incremental.py`.
- Readback client capability exists in `app/clients/data_read_client.py` as a read-only client for certified warehouse evidence.
- The repo has many tests around OHLCV ingestion, writer behavior, lineage, checkpoints, FMP, Polygon, safe DB persistence, and run state.

## Production Blockers

| Blocker | Severity | Why it blocks production | Exact file/module involved | Exact fix or verification required |
|---|---|---|---|---|
| No confirmed limited production activation path is wired end to end | CRITICAL | The repo has guarded persistence and planning flows, but not a clearly verified real production activation path for OHLCV ingestion | `app/ingestion/ohlcv/orchestrator.py`, `scripts/run_polygon_ohlcv_daily_update.py`, `scripts/run_polygon_ohlcv_chunked_backfill.py` | Verify one controlled production path end to end before expanding scope |
| Evidence contract is still explicitly planning-only | HIGH | The repo says the ingestion evidence contract is not enabled at runtime, so production evidence is not yet fully live | `scripts/diagnose_ingestion_evidence_output_contract.py` | Enable or formally verify the production evidence contract before relying on it for live operations |
| Single-symbol write plans can be misleading | HIGH | The plan object can report dry-run-oriented state even when a write is attempted, which weakens operator trust in the returned status | `app/ingestion/ohlcv/orchestrator.py` | Verify `write_mode`, write status, and lineage evidence are truthful under actual execution |
| Downstream readback is a client, not a proven closed loop | HIGH | The repo can request readback, but the certified serving implementation is outside this repository | `app/clients/data_read_client.py` | Verify readback against the downstream service before treating ingestion as production complete |
| Production DB schema contract is external and must be confirmed at runtime | HIGH | Writers and stores fail safe if the contract is missing, which is correct, but production activation still depends on external schema readiness | `app/writers/ohlcv_writer.py`, `app/state/ingestion_run_store.py`, `app/state/data_lineage_store.py`, `app/state/data_quality_result_store.py`, `app/state/manual_polygon_ohlcv_checkpoint_store.py` | Confirm tables, columns, and uniqueness constraints in the production database before first write |
| Multi-symbol production activation is still not ready | HIGH | The repo itself documents multi-symbol production as `NO_GO` | `docs/market_feature_bundle_multi_symbol_production_readiness_audit.md` | Leave multi-symbol activation blocked until a single-symbol production probe succeeds |
| The broader runbook ecosystem is still heavily planning-oriented | MEDIUM | Many scripts are intentionally read-only, diagnostic, or dry-run-only, which is correct for safety but not yet a production activation state | `scripts/diagnose_*`, `scripts/dry_run_*`, `scripts/preflight_*` | Keep these in place, but do not mistake them for a live production runtime |

## Dry-Run / Planning-Only Components

- `scripts/diagnose_ingestion_evidence_output_contract.py` is planning-only and explicitly disabled at runtime.
- The various `scripts/diagnose_*` readiness commands are diagnostics, not production execution.
- The `scripts/dry_run_*` commands are dry-run only by design.
- The `scripts/preflight_*` commands are read-only checks.
- The market-feature multi-symbol production audit remains `NO_GO`.
- The manual Polygon checkpoint and incremental paths are guarded and approval-gated rather than unattended production activation paths.

## Production-Like Components

- FMP fetch and retry classification are production-like enough to trust after vendor credential and endpoint verification.
- Polygon HTTP transport is production-like enough to trust after live endpoint and credential verification.
- OHLCV normalization is production-like and deterministic.
- The OHLCV writer is production-like because it checks schema, uniqueness, deduplicates input, and uses transactional write behavior.
- Run history, lineage, and quality persistence stores are production-like in their contract checks and fail-safe behavior.
- Manual checkpointing is production-like for controlled operator workflows.

## First Real Production Candidate

`FMP OHLCV single-symbol production write`

This is the safest first candidate because the repo already has a single-symbol orchestrator, deterministic normalization, guarded write behavior, and explicit run/lineage/checkpoint plumbing around that flow. It is still not ready to widen into multi-symbol production, but it is the smallest credible real production probe if schema and credentials are confirmed.

## Do Not Attempt Yet

- Do not run 10,000+ ticker ingestion yet.
- Do not broaden to a multi-symbol production run yet.
- Do not activate unattended scheduler execution yet.
- Do not start a full historical backfill yet.
- Do not wire AI Machine to unverified ingestion outputs yet.
- Do not treat planning-only diagnostics as production activation.

## Required Pre-Production Checklist

- Production DB target confirmed.
- Schema contract confirmed.
- Unique key confirmed.
- Backup/rollback approach confirmed.
- Vendor key confirmed without exposing secret.
- Symbol scope limited.
- Date range limited.
- Write mode truthful.
- Lineage/run evidence truthful.
- Readback verification available.
- Failure rollback behavior verified.
- Operator approval explicit.

## Recommended Next Command

`perform production DB schema contract verification`

## Required Statements

- No production action was performed in this update
- No live vendor call was performed in this update
- No production DB write was performed in this update
- Do not run 10,000+ ticker ingestion yet
- Do not activate unattended scheduler execution yet
- The next step must be a production activation decision, not another dry-run loop

