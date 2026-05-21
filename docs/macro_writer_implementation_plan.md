# Macro Writer Implementation Plan

This document is the implementation plan for a future writer that persists normalized FRED macro observations into `macro_rate_observations`.

## Authority

This plan is constrained by:

- `docs/writer_contracts.md`
- `docs/fred_macro_dry_run.md`
- `docs/data_contracts.md`
- `docs/codex_rules.md`
- `docs/macro_rate_observations_writer_contract.md` from `ai-market-machine-data`

`ai-market-machine-data` remains the schema owner. This repository may only implement the ingestion-side writer behavior after the external table contract is confirmed and approved.

## Goal

Write normalized FRED macro observations into `macro_rate_observations` without changing schema ownership, adding migrations, or introducing runtime persistence yet.

## Non-Goals

- no DB writes in this phase
- no SQL implementation
- no schema changes
- no migrations
- no pipeline persistence
- no AI, trading, signal, regime, strategy, portfolio, or risk logic

## Target Table

`macro_rate_observations`

## Natural Key

`series_id + observation_date + source`

This key is the deduplication and idempotency anchor for the writer.

## Proposed Row Mapping

The writer should map `NormalizedMacroObservation` to a canonical row using the following fields.

### Required columns

- `series_id`
- `observation_date`
- `source`
- `value`
- `vendor`
- `ingestion_run_id`
- `normalization_version`
- `quality_status`
- `created_at`
- `updated_at`

### Nullable columns

- `symbol`
- `symbol_id`
- `market_date`
- `timeframe`
- `adjusted`
- `vendor`
- `ingestion_run_id`
- `normalization_version`
- `quality_status`
- `updated_at`
- any contract-approved provenance fields such as notes, metadata, or lineage references if the external schema includes them

Note: the exact required/nullable split must be reconciled with the external `macro_rate_observations_writer_contract.md` before implementation. This plan assumes the writer-side row has the same operational shape as other ingestion-approved canonical rows and can carry lineage and quality context.

## Field Mapping From `NormalizedMacroObservation`

| NormalizedMacroObservation field | Target row field | Notes |
| --- | --- | --- |
| `symbol` | `symbol` | Preserve when present. |
| `symbol_id` | `symbol_id` | Preserve when present. |
| `timestamp` | `observation_date` | Store the UTC-normalized observation date component, not the full timestamp, unless the external contract explicitly requires a timestamp column. |
| `market_date` | `market_date` | Preserve if already present. |
| `timeframe` | `timeframe` | Preserve if the target contract supports it. |
| `adjusted` | `adjusted` | Preserve explicit boolean contract when supported. |
| `value` | `value` | Numeric observation value or `null` for missing FRED data. |
| `vendor` | `vendor` | Expected to be `fred` for FRED macro observations. |
| `source` | `source` | Use the approved source label from the normalized record. |
| `ingestion_run_id` | `ingestion_run_id` | Preserve run tracking. |
| `normalization_version` | `normalization_version` | Preserve transformation provenance. |
| `quality_status` | `quality_status` | Preserve validation outcome. |

## FRED "." Missing Values

FRED `"."` means the observation is missing or unavailable.

Proposed handling:

- map `"."` to `NULL` in the canonical `value` column
- preserve the observation row if the external contract permits missing values
- record a quality result for the row or batch so missing data remains visible
- do not reinterpret `"."` as zero
- do not coerce `"."` into a trading or signal meaning

If the external table contract rejects null values for `value`, the implementation must fail the row with a clear validation error and leave the writer behavior explicit rather than guessing.

## Idempotency Policy Proposal

The writer should be idempotent by natural key.

Proposed policy:

- treat `series_id + observation_date + source` as the canonical uniqueness rule
- on repeated writes with the same natural key and same normalized payload, perform no-op upserts
- on repeated writes with the same natural key but changed payload, apply deterministic conflict handling defined by the schema-owner contract

The default assumption should be "safe replay" because ingestion jobs and backfills may rerun.

## Duplicate Policy Proposal

- duplicate rows with the same natural key must not create multiple canonical records
- duplicates inside the same batch should be collapsed before persistence
- duplicates already present in the target table should resolve through a single row per natural key
- if the payload differs for the same key, the writer should fail the batch or isolate the conflict according to the external contract, rather than silently choosing an arbitrary winner

## Transaction Policy

- write each batch in a single transaction
- commit only after validation, duplicate resolution, and row mapping complete
- rollback the full batch on unexpected persistence errors
- do not partially persist a batch unless the external contract explicitly allows a documented partial-failure mode

## Batch Write Policy

- process normalized macro observations in bounded batches
- validate the full batch before opening the write transaction when possible
- deduplicate in memory by natural key before persistence
- preserve stable ordering for deterministic retries
- record batch-level counts for written, skipped, duplicate, and failed rows

## Error Handling Policy

- missing required fields should raise a validation error before DB access
- invalid numeric conversion should fail the affected row or batch explicitly
- database constraint violations should be surfaced with enough context to identify `series_id`, `observation_date`, and `source`
- transient DB failures should be retryable at the job orchestration layer, not hidden inside the writer
- vendor or AI logic must not be introduced as part of error handling

## Railway `DATABASE_URL` Considerations

The Railway deployment foundation already supports a safe runtime path that can validate config shape without opening a database connection.

For the writer implementation:

- require `DATABASE_URL` only when the writer is invoked
- do not connect during import or service startup
- do not require `DATABASE_URL` for the healthcheck path
- if `DATABASE_URL` is present, validate it before attempting a transaction
- if `DATABASE_URL` is absent, fail the writer invocation cleanly and explicitly

## Tests Needed Before Implementation

Before any DB write code is added, tests should cover:

- mapping from `NormalizedMacroObservation` to canonical row shape
- FRED `"."` to `NULL` handling
- deduplication by `series_id + observation_date + source`
- duplicate conflict behavior for same-key, different-value cases
- required-field validation failures
- batch transaction rollback behavior
- retryable vs non-retryable error classification
- no write attempt when `DATABASE_URL` is absent
- no import-time DB connection or vendor call behavior
- Railway start and health behavior remains unchanged

## Implementation Sequence

1. Confirm the external `macro_rate_observations` contract with `ai-market-machine-data`.
2. Define the canonical row adapter in ingestion.
3. Add unit tests for mapping and missing-value handling.
4. Add writer skeleton behavior without enabling live persistence.
5. Implement transaction-scoped batch writes only after contract approval.

## Boundary Reminder

`ai-market-machine-data` remains the schema owner. This repository is responsible only for ingestion-side writer behavior that respects the approved contract.
