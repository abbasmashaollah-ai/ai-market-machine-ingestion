# Market Feature Bundle Production Writer Activation Plan

## Purpose

- Define the gates before any production `market_feature_bundle` writes
- Keep production writes disabled until explicit approval
- Ensure monitoring exists before scheduler/backfill
- Keep AI Machine consumption last

## Preconditions

- Data repo production DB migrated to `0020_market_feature_bundle_snapshots`
- protected data route healthy
- safe test DB writer validation passed
- end-to-end read-after-write verification passed
- observability plan exists
- credentials and tokens are stored only in deployment secrets and variables
- exposed test DB credential rotated, deleted, or recreated

## Required production safety gates

- explicit user approval
- production target confirmation
- dry-run result reviewed
- write limit set to one controlled row for pilot
- no scheduler/backfill activation
- no vendor live fetch unless separately approved
- rollback and cleanup plan approved
- monitoring checklist approved

## Production pilot scope

- one universe
- SPY
- one dataset_version
- one controlled write
- verify row count delta
- verify data route read-back
- verify certification_status and validation_status
- verify lineage_refs and quality_result_refs handling
- no repeated automation

## Rollback and cleanup plan

- cleanup only by `idempotency_key`
- no broad deletes
- no truncate
- no drop table
- no migrations from ingestion repo
- record whether cleanup was run
- preserve row if approved as first production evidence row

## Monitoring requirements before activation

- writer success and failure logging
- conflict and idempotent-noop logging
- `last_successful_write_at`
- route health
- row count
- certification and validation status
- error alert candidates
- credentials redacted
- no secrets in logs

## Environment and secret rules

- no hardcoded DB URLs
- no committing credentials
- no printing full URLs
- use deployment secrets only
- separate test and production variables
- production `DATABASE_URL` must not be reused as a test URL

## Non-goals

- no production write in this planning step
- no scheduler activation
- no backfill
- no vendor live fetch
- no AI Machine changes
- no judge posture
- no trading decision
- no risk posture
- no portfolio logic

## Approval decision states

- `BLOCKED_PENDING_APPROVAL`
- `APPROVED_FOR_ONE_ROW_PRODUCTION_PILOT`
- `BLOCKED_BY_MONITORING_GAP`
- `BLOCKED_BY_ROUTE_OR_SCHEMA_GAP`

## Next steps after approval

- one-row production pilot command and checklist
- production pilot completion checkpoint after the approved one-row run
- production verification checkpoint
- monitoring checkpoint
- production route preservation verification after the preserved row is visible
- scheduler/backfill planning only after pilot
- AI Machine consumption remains last
