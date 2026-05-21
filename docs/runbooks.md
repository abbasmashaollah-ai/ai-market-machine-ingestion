# Runbooks

These are placeholder operational runbooks for ingestion failures.

Hard rule: never fix ingestion failures by weakening quality checks, bypassing writers, manually altering canonical schema, or adding AI/trading logic.

## 1. Daily Update Failure

- Symptoms: scheduled daily ingestion does not complete, run status is failed or missing, downstream data does not advance.
- Likely causes: vendor outage, credential issue, checkpoint corruption, writer failure, validation failure.
- Immediate checks: latest run status, logs, checkpoint state, vendor connectivity, database health.
- Safe actions: retry after identifying the failure point, preserve checkpoints, record the failure reason, rerun only through approved ingestion flow.
- Escalation notes: escalate if repeated failures affect more than one vendor or persist across retries.
- What not to do: do not bypass validation, skip lineage, or write directly to canonical tables.

## 2. Backfill Failure

- Symptoms: backfill job stops before the requested range completes, partial historical coverage, missing data windows.
- Likely causes: checkpoint mismatch, vendor API limits, data gaps, database constraints, write failure.
- Immediate checks: requested date range, checkpoint coverage, run history, quality outcomes, vendor response patterns.
- Safe actions: resume from the last valid checkpoint, rerun the backfill in the approved window, preserve error and lineage records.
- Escalation notes: escalate if the backfill repeatedly fails at the same boundary or produces inconsistent results.
- What not to do: do not disable idempotency, manually patch canonical rows, or weaken quality thresholds.

## 3. Stuck Checkpoint

- Symptoms: checkpoint does not advance, repeated runs resume from the same position, progress appears frozen.
- Likely causes: stale state, failed write, vendor pagination issue, lock contention, unexpected empty response.
- Immediate checks: checkpoint record, run logs, writer status, vendor response, last successful batch.
- Safe actions: confirm the checkpoint is valid, clear only stale operational state through approved tooling, rerun from the stored checkpoint.
- Escalation notes: escalate if the checkpoint cannot advance after confirming the source is healthy.
- What not to do: do not reset canonical tables or manually edit checkpoint state outside approved procedures.

## 4. Vendor API Outage

- Symptoms: request timeouts, 5xx responses, empty vendor availability, repeated connection failures.
- Likely causes: vendor outage, rate limiting, expired credentials, network issues, vendor maintenance.
- Immediate checks: vendor status, auth validity, retry logs, request volume, rate-limit headers if available.
- Safe actions: pause retries if the vendor is unavailable, retain checkpoints, record the outage, resume when the source recovers.
- Escalation notes: escalate if the outage threatens SLA or affects multiple vendor feeds.
- What not to do: do not invent fallback data, bypass vendor validation, or infer missing market data.

## 5. Database Write Failure

- Symptoms: approved records are not persisted, writer errors, transaction failures, constraint violations.
- Likely causes: connectivity issue, deadlock, schema mismatch in downstream contract, transient database instability.
- Immediate checks: writer logs, database health, transaction error details, affected table, retry history.
- Safe actions: retry through writers, preserve operational error records, verify idempotency before rerun.
- Escalation notes: escalate if the failure persists or indicates a contract mismatch with the approved schema.
- What not to do: do not write around the writer layer, do not alter schema locally, do not disable constraints.

## 6. Excessive Quality Failures

- Symptoms: large fraction of records fail validation, quality result volume spikes, approved output drops.
- Likely causes: vendor data drift, broken normalization, malformed payloads, upstream schema change.
- Immediate checks: failed rule names, sample payloads, vendor change indicators, normalization output, quality logs.
- Safe actions: keep failed records out of approved writes, record quality outcomes, isolate the source of failure, pause affected feeds if necessary.
- Escalation notes: escalate when a vendor-wide drift or parsing regression is confirmed.
- What not to do: do not weaken quality rules to force throughput, and do not silently accept failing records.

## 7. Zero Rows Written for Active Symbols

- Symptoms: the pipeline runs successfully but writes no approved rows for symbols expected to have data.
- Likely causes: symbol mapping issue, date boundary issue, vendor coverage gap, overly strict filters, checkpoint mismatch.
- Immediate checks: active symbol set, symbol mapping, vendor availability, date range, quality outcomes, reconciliation logs.
- Safe actions: confirm whether zero rows is legitimate, inspect normalization and reconciliation output, rerun only after root cause is understood.
- Escalation notes: escalate if the issue affects active symbols across multiple vendors or persists over multiple runs.
- What not to do: do not fabricate rows, relax approval criteria without review, or bypass reconciliation.

## 8. Ingestion Lag Above Threshold

- Symptoms: ingestion completes later than expected, checkpoint lags behind schedule, downstream freshness degrades.
- Likely causes: vendor slowness, rate limiting, large backfill, database latency, repeated retries, quality bottlenecks.
- Immediate checks: current lag, run duration, retry count, vendor response times, database write timing, checkpoint age.
- Safe actions: identify the bottleneck, reduce load through approved scheduling or batching settings, preserve operational state, keep approved writes intact.
- Escalation notes: escalate if freshness SLAs are at risk or lag increases without an obvious external cause.
- What not to do: do not skip validation, bypass writers, or introduce speculative intelligence to “predict” missing data.
