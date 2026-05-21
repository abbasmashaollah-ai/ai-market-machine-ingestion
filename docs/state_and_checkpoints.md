# State And Checkpoints

The state layer defines the ingestion job, checkpoint, run, and error contracts.

## Scope

This layer provides:

- job status enums and job dataclasses
- checkpoint dataclasses and checkpoint store protocols
- run dataclasses and summary helpers
- structured ingestion error records

## Boundary

This layer does not:

- persist data
- execute SQL
- write to the database
- implement writers
- call vendor APIs
- run ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- Status values are explicit and limited to ingestion operations.
- Checkpoint contracts are shaped for future idempotent backfill and resume behavior.
- Run records are intended to summarize execution without embedding persistence behavior.
