# Breadth Observations Handoff Dry-Run Validation

## Status
Local validation only. No production behavior changed.

## Purpose
Confirm the ingestion-side Breadth Observations JSONL handoff builder can produce a contract-aligned local artifact and evidence summary without vendor calls, scheduler activation, DB writes, or production rollout.

## Validation Summary
- A local JSONL handoff artifact is generated under the established `outputs/handoff/breadth/` pattern.
- Required contract-facing fields are present.
- The required contract-facing fields are present in the local artifact.
- Deterministic idempotency keys are stable.
- Invalid rows are rejected and can be quarantined locally.
- Derived and signal fields remain excluded from canonical top-level JSONL output.

## Evidence Fields Reported
- input row count
- accepted row count
- rejected/quarantined row count
- validation error summary
- idempotency key coverage
- source lineage summary
- schema version
- generated artifact path
- no-production-change statement

## No Production Statement
No vendor call was made, no download occurred, no scheduler was activated, no backfill ran, no production write occurred, and no production rollout is approved.
