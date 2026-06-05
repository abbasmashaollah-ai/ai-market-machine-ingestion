# Market Feature Bundle AI Machine Read-Consumption Contract

## Purpose

- define how AI Machine may consume market_feature_bundle later
- read-only consumption only
- data bundle is evidence, not judgment
- AI Machine consumption remains last until explicitly approved

## Source route

- `GET /internal/read/market-feature-bundle/{universe}`
- first approved universe: SPY
- certified_only default behavior
- protected/internal route only
- route owned by ai-market-machine-data

## Expected fields

- market_feature_bundle
- market_feature_bundle_coverage
- universe
- observation_date
- generated_at
- schema_version
- dataset_version
- compact_summary
- full_bundle_payload
- validation_status
- certification_status
- lineage_refs
- quality_result_refs
- coverage_status
- quality_status
- freshness_status
- missing_data_evidence
- stale_data_evidence
- warnings

## Consumption gates

- certification_status must be CERTIFIED
- validation_status must be PASS
- coverage_status should be COMPLETE
- quality_status should be PASS
- missing_data_evidence should be empty
- stale_data_evidence should be empty or handled explicitly
- schema_version must be supported
- dataset_version must be logged
- AI Machine must not consume if route returns 500/401/403
- AI Machine must treat missing-data response as no evidence, not as negative evidence

## Boundary rules

- AI Machine may interpret evidence
- AI Machine owns judgment/posture/decision logic
- ingestion/data must not emit judge posture
- ingestion/data must not emit trading decision
- ingestion/data must not emit risk posture
- ingestion/data must not emit portfolio allocation
- no portfolio allocation
- ingestion/data must not mutate AI Machine state
- no write-back from AI Machine to ingestion/data in this contract

## First consumption mode

- read-only shadow consumption
- no capital impact
- no execution impact
- no portfolio changes
- no user-facing trading recommendation
- log-only comparison against existing AI Machine internal state if later approved

## Failure handling

- route failure means skip bundle consumption
- uncertified bundle means skip bundle consumption
- validation failure means skip bundle consumption
- unsupported schema_version means skip bundle consumption
- missing row means no evidence available
- stale row means degraded/blocked depending on policy
- never infer a buy/sell/hold from missing data

## Audit and logging requirements

- log universe
- observation_date
- generated_at
- schema_version
- dataset_version
- certification_status
- validation_status
- coverage_status
- quality_status
- idempotency_key_prefix only
- do not log token
- do not log DB URL
- do not log full idempotency_key

## Non-goals

- no AI Machine code in this step
- no scheduler activation
- no backfill
- no vendor live fetch
- no production write
- no judge posture
- no trading decision
- no risk posture
- no portfolio logic
- no execution logic

## Next recommended phase

- AI Machine read-consumption implementation plan can be created later in ai-market-machine repo
- keep scheduler/backfill blocked until explicit approval
- continue monitoring preserved production row
