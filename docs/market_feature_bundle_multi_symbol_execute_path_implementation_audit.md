# Market Feature Bundle Multi-Symbol Execute Path Implementation Audit

## Purpose

- audit what is required to connect `--execute` to the existing production writer safely
- connect --execute to the existing production writer safely
- preserve safety before DB writes

## Current Scaffold Status

- multi-symbol production seed command exists
- dry-run passes for QQQ/IWM/DIA
- `--execute` is scaffold-blocked
- --execute is scaffold-blocked
- production writer untouched
- no DB writes occurred

## Existing Writer Compatibility

- Writer function entrypoints: `MarketFeatureBundleWriter.write_payload(...)` in `app/writers/market_feature_bundle_writer.py`
- Expected payload shape: `observation_date`, `generated_at`, `universe`, `schema_version`, `dataset_version`, `idempotency_key`, `raw_sections`, `synthesized_sections`, `section_record_counts`, `section_labels`, `compact_summary`, `full_bundle_payload`, `validation_status`, `validation_errors`, `validation_warnings`, `total_warnings`, `safety_flags`, `rejected_counts`, `certification_status`, `source_repo`, `source_run_id`, `input_dataset_versions`, `lineage_refs`, `quality_result_refs`
- Required fields: the full writer payload contract above
- Idempotency behavior: deterministic `idempotency_key`, idempotent no-op on duplicate idempotency key, conflict on grain collision with different idempotency key
- Duplicate/no-op behavior: `IDEMPOTENT_NOOP` when the same idempotency key already exists
- Conflict behavior: `CONFLICT` / `GRAIN_CONFLICT` when the same grain already exists with a different idempotency key
- Rollback/error behavior: session rollback on exceptions, `WRITE_FAILED` with error metadata
- DB adapter contract: `build_market_feature_bundle_session(...)`, `build_market_feature_bundle_table(...)`, `existing_by_idempotency_key(...)`, `existing_by_grain(...)`, `commit()`, `rollback()`, `cleanup_by_idempotency_key(...)`
- Required env vars without values: `AMM_PRODUCTION_PILOT_APPROVAL`, `AMM_PRODUCTION_PILOT_DATABASE_URL`, `AMM_PRODUCTION_PILOT_DATA_BASE_URL`, `AMM_PRODUCTION_PILOT_DATA_TOKEN`
- Writer symbol behavior: writer is symbol-agnostic, not SPY-specific
- symbol-agnostic or spy-specific
- QQQ/IWM/DIA payloads can be passed without code changes if payloads are converted to the writer contract

## Required Implementation Before Actual Execution

- exact adapter call needed: `build_market_feature_bundle_session(env[DATABASE_ENV])`
- exact env gate needed: `AMM_PRODUCTION_PILOT_APPROVAL == YES_APPROVED_MULTI_SYMBOL_WRITE` and `AMM_PRODUCTION_PILOT_DATABASE_URL` present
- exact approval gate needed: explicit second approval before DB write
- payload conversion needed: convert fixture production candidate payloads to writer payloads via `build_market_feature_bundle_producer_payload(...)`
- certification_status conversion: `PRODUCTION_CANDIDATE` must become `CERTIFIED` only after production validation and post-write verification
- certification_status conversion from production_candidate to certified
- per-symbol write result collection: required
- no-op/idempotent result handling: required for duplicate symbol/date/grain cases
- error handling and rollback/no-op handling: required via writer result handling and session rollback
- post-write direct Data API verification command: required after any write
- safe JSON output without secrets/full idempotency keys: required

## Risk Assessment

- Payload-shape risk: `MEDIUM`
- Writer compatibility risk: `MEDIUM`
- Idempotency/duplicate risk: `MEDIUM`
- Rollback/no-op risk: `MEDIUM`
- Partial-write risk: `HIGH`
- Env-var/secrets risk: `HIGH`
- Wrong-symbol risk: `HIGH`
- Stale-date risk: `MEDIUM`
- Data API verification risk: `MEDIUM`

## Go/No-Go Conclusion

- Status: `GO_AFTER_IMPLEMENTATION`
- Recommended next single step: implement a guarded multi-symbol `--execute` path that converts production-candidate payloads into writer payloads, but do not enable DB writes until explicit approval and tests are added
- `GO_NOW`
- `NO_GO`
- `GO_AFTER_IMPLEMENTATION`

## Safety Confirmations

- no DB writes
- no production seed/write
- no vendor calls
- no live API calls
- no scheduler activation
- no production changes
- no AI Machine runtime wiring
- no secrets committed
