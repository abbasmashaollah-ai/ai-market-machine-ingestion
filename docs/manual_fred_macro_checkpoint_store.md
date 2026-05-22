# Manual FRED Macro Checkpoint Store

`app/state/manual_fred_macro_checkpoint_store.py` provides the runtime checkpoint read/write support for manual FRED macro incremental runs.

## Scope

The store:

- reads checkpoint state by checkpoint key
- writes checkpoint state only through the approved checkpoint contract
- updates `last_successful_observation_date` after successful confirmed writes
- fails safely if the expected checkpoint table or columns are unavailable

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

`ai-market-machine-data` remains the schema owner.

