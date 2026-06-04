# Market Feature Bundle Safe Test DB Integration Plan
Stage E.2
app/features remains calculation-only

## Purpose

- Validate `MarketFeatureBundleWriter` against a safe test DB only
- Still no production writes
- Still no scheduler/backfill
- Still no AI Machine changes

## Environment variable gate

- Use `AMM_TEST_DATABASE_URL` or `AMM_INGESTION_TEST_DATABASE_URL`
- Skip the test if neither variable is present
- Reject production-looking hostnames unless explicitly allowlisted
- Credentials must be redacted in output
- Never print full connection strings

## DB target contract

- Target table: `market_feature_bundle_snapshots`
- Table is owned by `ai-market-machine-data`
- Ingestion writer must match the data repo schema exactly
- No schema changes from ingestion repo

## Test flow

- Build fixture market feature bundle
- Build producer payload
- Use writer in `dry_run=False` only against safe test DB
- dry_run=False only against safe test DB
- Insert or upsert one test payload
- Verify idempotency duplicate behavior
- Verify grain conflict behavior
- Verify row can be read back
- Cleanup test row by `idempotency_key` only
- cleanup test row by idempotency_key only
- Never touch production rows

## Safety behavior

- No vendor calls
- No live external API calls
- No scheduler activation
- No seed rows
- No broad deletes
- No truncate
- No drop table
- No migrations from ingestion repo
- No data repo modifications

## Writer implementation requirements for future E.2

- DB adapter should live outside `app/features`
- Stage E.2 adapter path: `app/writers/market_feature_bundle_db_adapter.py`
- Likely `app/writers/market_feature_bundle_db_adapter.py` or `app/writers/market_feature_bundle_sqlalchemy_adapter.py`
- Adapter may own SQLAlchemy/session details, but only after approval
- `MarketFeatureBundleWriter` should remain injectable and testable
- `app/features` remains calculation-only

## Approval gates before E.2 implementation

- Explicit user approval
- Safe test DB URL configured
- Target DB confirmed migrated to `0020`
- target db confirmed migrated to 0020
- Cleanup strategy approved
- Production writes blocked by default

## Non-goals

- No DB integration in this planning step
- No DB writes
- No vendor calls
- No scheduler activation
- No AI Machine changes
- No judge posture
- No trading decision
- No risk posture
- No portfolio logic
