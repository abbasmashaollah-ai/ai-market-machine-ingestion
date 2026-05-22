# Manual FRED Macro Checkpoint Inspection

`scripts/inspect_fred_macro_checkpoint.py` is a read-only operator tool for inspecting the stored checkpoint state used by manual FRED macro incremental persistence.

## Scope

The command:

- accepts `--series-id`
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

- `checkpoint_found`
- `checkpoint_key`
- `series_id`
- `status`
- `planned_start_date`
- `planned_end_date`
- `last_successful_observation_date`
- `updated_at`

## Safety

The command is read-only. It is intended for manual verification before running confirmed persistence commands.

`ai-market-machine-data` remains the schema owner.
