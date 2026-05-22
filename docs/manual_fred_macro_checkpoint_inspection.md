# Manual FRED Macro Checkpoint Inspection

`scripts/inspect_fred_macro_checkpoint.py` is a read-only operator tool for inspecting the stored checkpoint state used by manual FRED macro incremental persistence.

## Scope

The command:

- accepts `--series-id`
- accepts repeated `--series-id`
- accepts `--category`
- accepts `--all`
- accepts `--start-date`
- accepts `--end-date`
- computes the same checkpoint key used by the manual persistence command
- reads checkpoint state through `ManualFREDMacroCheckpointStore`
- prints only safe fields

It does not:

- call FRED
- write to the database
- persist checkpoints
- schedule work
- require `FRED_API_KEY`
- print `DATABASE_URL`

`DATABASE_URL` is required because the command reads checkpoint state from the approved checkpoint table contract.

## Printed Fields

The command prints:

- one safe checkpoint line per selected series
- `checkpoint_found`
- `checkpoint_key`
- `series_id`
- `status`
- `planned_start_date`
- `planned_end_date`
- `last_successful_observation_date`
- `updated_at`
- one aggregate line with `checkpoint_total` and `checkpoint_found_total`

## Safety

The command is read-only. It is intended for manual verification before running confirmed persistence commands.

`ai-market-machine-data` remains the schema owner.

## Verification Log

- Initial inspection confirmed `checkpoint_found=true`
- Initial checkpoint key: `fred:macro_observations:GDP:1d:2025-01-01:2025-12-31`
- Initial status: `completed`
- Initial `last_successful_observation_date=2025-10-01`
- Final inspection confirmed the checkpoint remained unchanged after the resumed persistence verification
- Final `updated_at` remained unchanged
- Final `last_successful_observation_date` remained `2025-10-01`
- Live multi-series checkpoint verification completed with:
  - command: `python -m scripts.inspect_fred_macro_checkpoint --series-id GDP --series-id UNRATE --start-date 2025-01-01 --end-date 2025-12-31`
  - `checkpoint_total=2`
  - `checkpoint_found_total=2`
  - GDP: `checkpoint_found=true`, `last_successful_observation_date=2025-10-01`
  - UNRATE: `checkpoint_found=true`, `last_successful_observation_date=2025-12-01`
