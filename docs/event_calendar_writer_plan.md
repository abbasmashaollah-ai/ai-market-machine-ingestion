# Event Calendar Writer Plan

This is the writer-readiness plan for the event calendar slice.
It describes future write behavior only. Persistence remains deferred until the data-side contract and writer boundary are approved.

## Future Writer Responsibilities

The future writer, if approved, would:

- accept normalized event calendar records
- validate the record shape against the canonical contract
- enforce the approved uniqueness key
- stage records for a confirmed write only after validation passes
- record run, quality, and lineage outcomes for write attempts
- return structured batch results for successes and failures

## Uniqueness Rule

The preferred unique key is:

- `event_id`

If a stable `event_id` is not available, the fallback uniqueness expectation is:

- `event_type + event_date + source + symbol`

The fallback treats `symbol` as nullable for non-symbol-specific events.

## Confirmed-Write Gating

Writes must remain gated until:

- the canonical event calendar contract is approved
- the writer contract is approved
- the target table and migration path are approved in `ai-market-machine-data`
- quality checks pass for the batch
- lineage capture is available for the batch

No write should be attempted without an explicit confirmed-write decision.

## Batch Commit and Rollback Expectations

- Commit batches only after validation and gating succeed.
- Roll back the batch if any required contract check fails.
- Do not partially acknowledge a batch as written if the batch commit fails.
- Surface batch-level write outcomes separately from record-level validation failures.

## Recording Expectations

Future writer execution should record:

- run metadata
- quality results
- lineage references
- write outcome summaries

These recordings remain future responsibilities and are not active persistence behavior in this repository.

## Boundary

`ai-market-machine-ingestion` does not own schema design, migrations, or canonical persistence for the event calendar.
This plan is read-only and does not enable database writes.

