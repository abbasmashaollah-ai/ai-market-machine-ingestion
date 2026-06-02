# Volatility Index Observations Writer Handoff Contract

Purpose:
- define the ingestion-side writer handoff contract for `volatility_index_observations`
- keep the producer boundary separate from persistence, vendor access, and scheduler activation
- document the exact payload shape the writer must accept after dry-run validation

Producer module:
- `app/ingestion/volatility/observations_producer.py`

Target table:
- `ai-market-machine-data.volatility_index_observations`

Starter series:
- `VIX`
- `VVIX`
- `VXN`
- `RVX`

Required payload fields:
- `symbol`
- `index_family`
- `observation_date`
- `timestamp`
- `value`
- `close`
- `source`
- `source_symbol`
- `source_attribution`
- `daily_or_intraday`
- `lineage`
- `quality_status`
- `certification_status`
- `freshness_status`
- `freshness_checked_at`
- `evidence`

Accepted payload shape:
- JSON-serializable dictionary records emitted by the dry-run producer
- canonical symbol rows with source provenance preserved
- idempotent observation rows keyed for warehouse uniqueness on `symbol + index_family + observation_date + source`
- payloads that already passed producer validation and carry lineage/evidence metadata

Rejected payload behavior:
- records missing required fields must be rejected before handoff
- rejected payloads must not be sent to a writer
- rejected payloads should carry explicit error details back to the caller
- malformed or unsupported records must not trigger DB writes, vendor retries, or scheduler actions

Idempotency expectations:
- repeated dry-run output for the same observation must produce the same writer handoff key
- writer-level deduplication should respect the warehouse uniqueness expectation of `symbol + index_family + observation_date + source`
- source revisions must remain traceable through lineage and evidence rather than silently collapsing provenance

Uniqueness expectation:
- the data-repo table contract is expected to enforce uniqueness on `symbol + index_family + observation_date + source`
- writer logic should use that key when deciding conflict handling, dedupe, or replay behavior

Writer responsibility:
- validate the final handoff shape before persistence
- upsert or reject according to the approved data-repo contract
- preserve lineage, evidence, quality, certification, and freshness metadata
- keep ingestion-side canonicalization stable across retries and backfills

Dry-run versus write mode:
- dry-run mode produces validated payloads but does not persist them
- write mode is a later approval step and must be implemented only after the data-side contract is confirmed

Explicit non-goals for this step:
- no DB writes in this step
- no live vendor calls in this step
- no scheduler activation in this step
- no modification to `ai-market-machine-data`
- no modification to AI Machine
- no secrets exposure

Future implementation sequence:
1. Keep the dry-run producer contract stable and covered by tests.
2. Add a writer implementation only after the data-repo contract is approved.
3. Add conflict handling that matches the warehouse uniqueness expectation.
4. Add end-to-end persistence verification in a separate approved step.
5. Expose the data to downstream consumers only after persistence is stable.
