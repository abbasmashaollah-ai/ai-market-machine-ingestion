# Market Feature Bundle Real Writer Approval Plan

This is the Stage E planning checkpoint for market feature bundle persistence. It does not implement the writer.
real-writer approval plan
outside app/features
app/features remains calculation-only

## Current completed state

- data repo Stage 1-6 complete
- ingestion Stage A complete
- ingestion Stage B complete
- ingestion Stage C complete
- feature-engine boundary guardrail complete
- handoff checkpoint complete

## Future writer location decision

- real writer must live outside `app/features`
- preferred path: `app/writers/market_feature_bundle_writer.py`
- acceptable alternate path: `app/handoff/market_feature_bundle_handoff.py`
- `app/features` remains calculation-only

## Target contract

- target repo: `ai-market-machine-data`
- target table: `market_feature_bundle_snapshots`
- target route for verification: `GET /internal/read/market-feature-bundle/{universe}`
- target table already verified empty and route verified clean

## Real writer responsibilities

- accept producer payload from `build_market_feature_bundle_producer_payload(...)`
- validate required fields
- enforce deterministic `idempotency_key`
- write or upsert one row per `observation_date` + `universe` + `schema_version` + `dataset_version`
- preserve `full_bundle_payload`, `compact_summary`, `lineage_refs`, and `quality_result_refs`
- preserve `validation_status` and `certification_status`
- return a structured writer result
- never perform AI interpretation or trading judgment

## Idempotency and upsert plan

- primary guard: `idempotency_key`
- grain guard: `observation_date` + `universe` + `schema_version` + `dataset_version`
- repeated identical payload should not create duplicate rows
- changed `dataset_version` or changed payload checksum should create a distinct `idempotency_key` subject to grain rules
- conflicts must be explicit and test-covered

## Database safety plan

- real writer requires explicit approval before implementation
- real writer must be tested first against a safe test DB only
- production/Railway writes require separate approval
- credentials must never be printed
- connection strings must be redacted
- no seed rows in production
- no scheduler writes until writer is stable

## Test plan for future writer

- unit tests with fake/session stub
- safe test DB integration tests gated by environment variable
- idempotency duplicate tests
- conflict tests
- serialization tests
- no app/features persistence imports
- no vendor-call tests
- no scheduler tests

## Rollback and failure behavior

- no partial writes where possible
- transaction rollback on failure
- structured error result
- no retry loop in the first implementation
- no scheduler/backfill activation

## Non-goals

- no writer implementation in this planning step
- no DB writes
- no vendor calls
- no scheduler activation
- no data repo changes
- no AI Machine changes
- no judge posture
- no trading decision
- no portfolio logic
- no risk posture

## Approval gates before implementation

- explicit user approval
- safe test DB available or fake-session strategy approved
- writer path chosen
- idempotency conflict behavior approved
- test list approved
- production write path explicitly blocked by default

## Stage E.1 completion

- Stage E.1 real-writer skeleton is ready with fake/session-stub tests only
- production persistence is still blocked pending explicit approval

## Stage E.2 planning target

- safe test DB integration plan is next
- adapter path: `app/writers/market_feature_bundle_db_adapter.py`
- `MarketFeatureBundleWriter` remains injectable and testable
- production writes remain blocked by default
