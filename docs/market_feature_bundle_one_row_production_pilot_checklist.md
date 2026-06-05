# Market Feature Bundle One-Row Production Pilot Checklist

## Purpose

- Define the exact checklist before one controlled production row is written
- Keep production writes blocked until every checklist item is approved
- Keep scheduler and backfill disabled
- Keep AI Machine consumption last

## Preconditions

- Production data repo DB is confirmed migrated to `0020_market_feature_bundle_snapshots`
- protected data route is healthy
- safe test DB writer validation passed
- end-to-end read-after-write verification passed
- observability helpers exist
- observability event and summary can be generated for writer result
- production target has been explicitly confirmed
- exposed test DB credential has been rotated, deleted, or recreated

## Pilot scope

- One universe only: SPY
- One dataset_version only
- One controlled `market_feature_bundle` row
- One controlled market_feature_bundle row
- No scheduler
- No backfill
- No vendor live fetch unless separately approved
- No repeated automation

## Required dry-run before write

- Build fixture or approved source bundle
- Build producer payload
- Run writer in `dry_run=True`
- Inspect writer result
- Generate observability event
- Confirm validation_status and certification_status
- Confirm idempotency_key prefix
- Confirm target table `market_feature_bundle_snapshots`

## Required production write safeguards

- Explicit user approval
- Production DB target redacted and confirmed
- Production writes disabled by default until approval
- Credentials stored only in deployment or local secret env vars
- No full DB URL printed
- No secrets in logs
- Cleanup decision approved before write

## Verification after one-row write

- Verify write_status is WRITE_ACCEPTED or approved IDEMPOTENT_NOOP
- Verify row count delta
- Verify idempotency_key exists
- Verify protected route read-back:
  `GET /internal/read/market-feature-bundle/SPY`
- Verify structured fields:
  `idempotency_key`, `universe`, `schema_version`, `dataset_version`, `compact_summary`, `full_bundle_payload`, `validation_status`, `certification_status`, `lineage_refs`, `quality_result_refs`
- Verify observability event and summary

## Cleanup or preserve decision

- Decide before pilot whether to preserve the first production evidence row or clean it up
- If cleanup, cleanup only by `idempotency_key`
- No broad deletes
- No truncate
- No drop table
- Record cleanup result

## Rollback and failure behavior

- If write fails, stop
- If route read-back fails, stop and inspect
- No retry loop
- No scheduler activation
- No fallback to broad deletes
- Record failure checkpoint before continuing

## Non-goals

- No production write in this checklist step
- No scheduler activation
- No backfill
- No vendor live fetch
- No AI Machine changes
- No judge posture
- No trading decision
- No risk posture
- No portfolio logic

## Approval states

- `BLOCKED_PENDING_APPROVAL`
- `APPROVED_FOR_ONE_ROW_PRODUCTION_PILOT`
- `BLOCKED_BY_OBSERVABILITY_GAP`
- `BLOCKED_BY_ROUTE_OR_SCHEMA_GAP`
- `BLOCKED_BY_TARGET_CONFIRMATION_GAP`

## Next steps after successful pilot

- Production pilot completion checkpoint
- Production pilot completion checkpoint recorded in `docs/market_feature_bundle_one_row_production_pilot_completion_checkpoint.md`
- Monitoring checkpoint
- Scheduler and backfill planning only after pilot checkpoint
- AI Machine consumption remains last
