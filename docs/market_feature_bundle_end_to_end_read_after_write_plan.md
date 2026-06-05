# Market Feature Bundle End-to-End Read-After-Write Verification Plan

## Purpose

- Verify end-to-end handoff across ingestion writer and data read route
- Prove data written by ingestion can be read through the data repo protected private-read route
- Still safe-test-only
- Still no production activation

## Required prerequisites

- Data repo migrations applied through `0020_market_feature_bundle_snapshots` on the same safe test DB
- Ingestion safe writer test has passed
- Data repo app can be pointed to same safe test DB
- Protected route token/ops guard behavior understood
- Test row cleanup strategy approved
- Credentials redacted and not committed

## Environment variables

- Ingestion side: `AMM_INGESTION_TEST_DATABASE_URL` or `AMM_TEST_DATABASE_URL`
- Data side: `DATABASE_URL` pointed only at same safe test DB during verification
- Optional local route test settings if needed
- No production `DATABASE_URL`
- Variables removed after test

## Planned verification flow

- Build fixture market feature bundle
- Build producer payload with unique test `dataset_version`
- Write payload through ingestion writer adapter to safe test DB
- Start or call data repo app against same safe test DB
- Call `GET /internal/read/market-feature-bundle/{universe}`
- Verify route returns 200
- Verify `market_feature_bundle` is not `None`
- Verify `idempotency_key` matches
- Verify `compact_summary`/`full_bundle_payload` fields are present
- Verify `certification_status` and `validation_status` are preserved
- Cleanup by `idempotency_key` only
- cleanup by idempotency_key
- Verify route returns clean missing-data response or row is absent after cleanup
- Remove env vars

## Safety rules

- No production writes
- No seed rows
- No broad deletes
- No truncate
- No drop table
- No migrations from ingestion repo
- No vendor calls
- No scheduler activation
- No AI Machine changes
- No judge posture
- No trading decision
- No risk posture
- No portfolio logic

## Expected result

- One controlled test row is visible through the data repo protected route
- Duplicate/idempotency behavior remains safe
- Cleanup removes test row
- No persistent test data remains

## Failure handling

- Rollback/cleanup by `idempotency_key`
- Do not retry blindly
- Do not switch to production DB
- Record failure before proceeding

## Next step after successful end-to-end verification

- Production-write approval plan
- Monitoring/observability plan
- Controlled production pilot only after explicit approval
- AI Machine consumption remains last
