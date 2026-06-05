# Market Feature Bundle Production Monitoring Checkpoint

## Monitoring checkpoint summary

- production monitoring checkpoint created after successful one-row pilot
- preserved production row exists
- monitoring is required before scheduler/backfill
- AI Machine consumption remains last

## Known production row baseline

- universe SPY
- dataset_version production_pilot.v1
- schema_version market_feature_bundle.v1
- validation_status PASS
- certification_status CERTIFIED
- coverage_status COMPLETE
- quality_status PASS
- source_repo ai-market-machine-ingestion
- source_run_id production_pilot.v1
- row preserved under PRESERVE_FIRST_PRODUCTION_ROW

## Required monitoring fields

- latest market_feature_bundle row by universe
- snapshot_count by universe
- latest observation_date by universe
- latest generated_at by universe
- dataset_version
- schema_version
- validation_status
- certification_status
- coverage_status
- quality_status
- freshness_status
- missing_data_evidence
- stale_data_evidence
- warnings

## Writer monitoring fields

- write_attempt_count
- write_success_count
- write_failure_count
- status_distribution
- last_written_dataset_version
- last_written_universe
- idempotency_key_prefix only
- rollback_count
- conflict_count
- idempotent_noop_count

## Route monitoring fields

- protected route health
- `GET /internal/read/market-feature-bundle/SPY`
- route status code
- route latency
- certified_only behavior
- route read-back result
- missing-data response behavior

## Alert candidates

- no latest row for SPY
- certification_status not CERTIFIED
- validation_status not PASS
- coverage_status not COMPLETE
- quality_status not PASS
- route returns non-200
- row count unexpectedly decreases
- repeated writer failures
- conflict_count greater than expected
- scheduler/backfill attempts while disabled

## Operational boundaries

- no scheduler activation yet
- no backfill yet
- no vendor live fetch
- no AI Machine changes
- no data repo source changes
- no broad deletes
- no truncate
- no drop table
- cleanup only by idempotency_key if ever approved
- credentials redacted
- no secrets in logs

## Security and credential note

- production DB credential was exposed during setup
- rotate production DB credential
- never commit credentials
- never print token or DB URL
- only idempotency_key_prefix should appear in logs/checkpoints

## Credential verification continuity

- preserved production row survived credential rotation
- protected route verification passed after rotation
- ai-market-machine-data was redeployed or reconnected with updated credential
- no new ingestion write was needed

## Next recommended phase

- rotate exposed production DB credential
- define scheduler/backfill approval plan
- define AI Machine read-consumption contract later
- AI Machine consumption remains last
