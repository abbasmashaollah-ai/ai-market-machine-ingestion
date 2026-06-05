# Market Feature Bundle Observability Plan

- market_feature_bundle observability

## Purpose

- Define what must be monitored before production writes
- Define what must be monitored before scheduler/backfill activation
- Keep production writer activation blocked until observability requirements are approved

## Required writer metrics

- `write_attempt_count`
- `write_success_count`
- `write_failure_count`
- `idempotent_noop_count`
- `conflict_count`
- `rollback_count`
- `cleanup_success_count`
- `cleanup_failure_count`
- `last_successful_write_at`
- `last_failed_write_at`
- `last_written_dataset_version`
- `last_written_universe`

## Required data-quality and certification metrics

- validation_status distribution
- certification_status distribution
- total_warnings trend
- safety_flags status
- rejected_counts trend
- missing lineage_refs count
- missing quality_result_refs count

## Required warehouse/read metrics

- market_feature_bundle_snapshots row count
- `market_feature_bundle_snapshots` row count
- latest observation_date by universe
- latest generated_at by universe
- protected route success/failure
- protected route latency
- clean missing-data response count
- read-after-write verification result
- read-after-write verification result

## Required safety and ops checks

- production writes disabled by default
- scheduler disabled by default
- no broad deletes
- no truncate/drop table
- cleanup only by `idempotency_key`
- credentials redacted
- no secrets in logs
- feature engines remain calculation-only

## Alert candidates

- writer failures above threshold
- repeated conflicts
- no successful bundle write in expected window
- data route returns 500
- certification_status not CERTIFIED for latest bundle
- validation_status FAIL
- lineage and quality refs missing when required
- cleanup failure
- scheduler attempts while disabled

## Dashboard candidates

- writer health panel
- latest bundle freshness panel
- certification and validation panel
- route health panel
- DB row growth panel
- error and conflict panel
- scheduler disabled and enabled panel
- future Grafana and Prometheus dashboard ideas

## Logging requirements

- structured log fields
- idempotency_key prefix only
- universe
- dataset_version
- schema_version
- write_status
- validation_status
- certification_status
- error type
- redacted DB target
- no credentials

## Next implementation phases

- observability contract and checkpoint
- lightweight local structured logging
- metrics surface or health endpoint
- dashboard and export plan
- production writer approval
- scheduler and backfill only after monitoring exists
- AI Machine consumption remains last

## Non-goals

- no production writes in this planning step
- no scheduler activation
- no vendor calls
- no AI Machine changes
- no judge posture
- no trading decision
- no risk posture
- no portfolio logic
