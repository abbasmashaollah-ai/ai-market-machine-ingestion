# Manual FRED Macro Checkpoint Store

`app/state/manual_fred_macro_checkpoint_store.py` provides the runtime checkpoint read/write support for manual FRED macro incremental runs.

## Scope

The store:

- reads checkpoint state by checkpoint key
- writes checkpoint state only through the approved checkpoint contract
- updates `last_successful_observation_date` after successful confirmed writes
- fails safely if the expected checkpoint table or columns are unavailable
- adapts metadata for PostgreSQL JSON columns so psycopg2-compatible connections can persist it safely
- verified live against the manual incremental persistence flow with confirmed write and checkpoint update enabled

## Contract

The store works with the in-memory checkpoint shape documented in [docs/manual_fred_macro_checkpoint_contract.md](manual_fred_macro_checkpoint_contract.md).

## Safety

The store does not:

- create tables
- run migrations
- open a database connection on its own
- call vendor APIs
- schedule work
- own schema
- silently write raw Python dicts into JSON columns

`ai-market-machine-data` remains the schema owner.

## Verified Runtime Result

- manual checkpoint-enabled confirmed write completed successfully for `GDP`
- checkpoint metadata persisted without raw Python dict adaptation errors
- live table shape used: `checkpoint_id`, `vendor`, `dataset`, `symbol`, `timeframe`, `start_date`, `end_date`, `last_successful_date`, `status`, `attempt_count`, `created_at`, `updated_at`, `metadata`
- checkpoint store is also used for checkpoint-based resume behavior, advancing the effective start date to the day after `last_successful_date`
