# Market Feature Bundle Producer Contract

This document defines the Stage A producer contract for handing off fixture-mode market feature bundle evidence from `ai-market-machine-ingestion` to `ai-market-machine-data`.

## Handoff target

- Repository: `ai-market-machine-data`
- Warehouse table: `market_feature_bundle_snapshots`
- Protected read route: `GET /internal/read/market-feature-bundle/{universe}`
- Verified data repo checkpoint: `f9c4a9b Record market feature bundle stage 6 verification`

## Producer output fields

The producer output must be shaped to map to the data table with the following fields:

- `observation_date`
- `generated_at`
- `universe`
- `schema_version`
- `dataset_version`
- `idempotency_key`
- `raw_sections`
- `synthesized_sections`
- `section_record_counts`
- `section_labels`
- `compact_summary`
- `full_bundle_payload`
- `validation_status`
- `validation_errors`
- `validation_warnings`
- `total_warnings`
- `safety_flags`
- `rejected_counts`
- `certification_status`
- `source_repo`
- `source_run_id`
- `input_dataset_versions`
- `lineage_refs`
- `quality_result_refs`

## Idempotency

The handoff payload must use a deterministic `idempotency_key`.

Recommended key components:

- `observation_date`
- `universe`
- `schema_version`
- `dataset_version`
- bundle checksum

This key is the basis for avoiding duplicate writes once a writer stage is approved and implemented. No duplicate writes are expected from the later writer stage when the key is stable.

## Validation boundaries

- The bundle validator must pass before a handoff payload is eligible.
- `total_warnings` must be preserved.
- `safety_flags` must be preserved.
- `rejected_counts` must be preserved.
- Fixture-mode can produce contract-shaped payloads but must not persist them yet.

## Source and lineage boundaries

- `source_repo = ai-market-machine-ingestion`
- `source_run_id` is optional until real run store integration exists.
- `input_dataset_versions` is optional or empty in fixture mode.
- `lineage_refs` is optional or empty in fixture mode.
- `quality_result_refs` is optional or empty in fixture mode.

## Explicit non-goals

- no real writer
- no DB writes
- no vendor calls
- no scheduler activation
- no data repo changes
- no AI Machine changes
- no judge posture
- no trading decision
- no production persistence

## Next ingestion stages

- Stage B: Dry-run producer payload builder
- Stage C: Mock writer handoff
- Stage D: Live-source dry-run only if approved
- Stage E: Real writer / persistence only after approval
- Stage F: Scheduler/backfill activation only after writer is stable

