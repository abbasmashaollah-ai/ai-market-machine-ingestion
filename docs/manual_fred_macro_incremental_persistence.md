# Manual FRED Macro Incremental Persistence

`scripts/persist_fred_macro_incremental.py` is a manual command for fetching incremental FRED macro observations, normalizing them, validating them, and optionally writing valid rows through `app/writers/macro_writer.py`.

## Scope

The CLI:

- accepts `--series-id`
- accepts `--category`
- accepts `--all`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--confirm-write`
- requires `FRED_API_KEY`
- requires `DATABASE_URL` only when `--confirm-write` is used
- uses the existing manual incremental selection and dry-run fetch/validate flow
- writes only through `MacroWriter`
- supports `--use-checkpoint` to read an existing checkpoint contract
- supports `--update-checkpoint` to persist last successful observation metadata after confirmed successful writes

## Output

Each series summary prints:

- `series_id`
- `requested_start_date`
- `effective_start_date`
- `rows_fetched`
- `rows_valid`
- `rows_invalid`
- `rows_written`
- `validation_failures`
- `planned_start_date`
- `planned_end_date`
- `write_confirmed`
- `status`

## Safety

Without `--confirm-write`, the command performs fetch, normalize, and validate only.

With `--confirm-write`, it writes only valid observations through the approved macro writer.

Checkpoint updates only happen when both `--confirm-write` and `--update-checkpoint` are present and the write succeeds.

When `--use-checkpoint` is enabled and the stored checkpoint has a `last_successful_observation_date`, the command resumes from the next day. If that effective start date is after the requested end date, the command skips safely, reports zero rows, and does not update the checkpoint.

When resumed fetches still return rows at or before the stored `last_successful_observation_date`, those rows are filtered out before validation and write. If nothing remains after filtering, the command reports `skipped_already_current`, writes nothing, and does not update the checkpoint.

The command does not:

- create tables
- run migrations
- persist checkpoints
- schedule work
- run automatically on Railway startup
- create or alter schema

Checkpoint persistence is a read/write operation against the approved checkpoint contract only. If the expected checkpoint table or columns are unavailable, the command fails safely with a clear message.

`ai-market-machine-data` remains the schema owner.

## Production Verification Log

- Verified the manual command inventory with `python -m scripts.verify_manual_ingestion_commands`
- Ran the dry persistence preview for `GDP` over `2025-01-01` to `2025-12-31`
- Confirmed write was skipped because `DATABASE_URL` was not configured locally
- No database row-count verification was performed in this environment because the confirmed-write path was not available
- Readiness check passed with `dry_run_ready=true`, `confirmed_write_ready=true`, and `missing=[]`
- Confirmed command: `python -m scripts.persist_fred_macro_incremental --series-id GDP --start-date 2025-01-01 --end-date 2025-12-31 --confirm-write`
- Result: `rows_fetched=4`, `rows_valid=4`, `rows_invalid=0`, `rows_written=4`, `validation_failures=0`, `write_confirmed=true`
- Dry checkpoint load with `--use-checkpoint` failed safely because the checkpoint table contract is not available yet in this environment: missing `checkpoint_id` and `metadata` columns on `ingestion_checkpoints`
- Checkpoint metadata persistence is now JSON-adapted for psycopg/Postgres-compatible execution when the approved checkpoint contract is available
- Checkpoint-enabled confirmed write now succeeds with `--use-checkpoint --update-checkpoint` and writes `rows_written=4` for `GDP` over `2025-01-01` to `2025-12-31`
- Checkpoint resume behavior now advances the effective start date by one day after `last_successful_observation_date`
- Manual resumed runs now report both `requested_start_date=2025-01-01` and `effective_start_date=2025-10-02` for `GDP`, showing checkpoint-based trimming of the fetch window
- Checkpoint verification is available through `python -m scripts.inspect_fred_macro_checkpoint --series-id GDP --start-date 2025-01-01 --end-date 2025-12-31`
- Live resume verification confirmed the checkpoint was already current:
  - `requested_start_date=2025-01-01`
  - `effective_start_date=2025-10-02`
  - `rows_fetched=0`
  - `rows_valid=0`
  - `rows_invalid=0`
  - `rows_written=0`
  - `validation_failures=0`
  - `write_confirmed=true`
  - `status=skipped_already_current`
- Final inspection confirmed the checkpoint remained unchanged:
  - `checkpoint_found=true`
  - `checkpoint_key=fred:macro_observations:GDP:1d:2025-01-01:2025-12-31`
  - `updated_at` unchanged
  - `last_successful_observation_date=2025-10-01`

## Readiness Diagnostic

Use `python -m scripts.check_manual_fred_persistence_readiness` to check whether the environment is ready for a manual confirmed write without opening a database connection or printing secrets.

## Checkpoint Contract

See [docs/manual_fred_macro_checkpoint_contract.md](manual_fred_macro_checkpoint_contract.md) for the in-memory checkpoint shape that the manual checkpoint store reads and writes through the approved checkpoint table contract.
