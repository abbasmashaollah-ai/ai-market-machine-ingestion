# Breadth Observations Ingestion Handoff Builder Discovery

## Status
Discovery only. No runtime implementation was added.

## Purpose
Determine whether ingestion already has a Breadth Observations JSONL handoff builder or a close equivalent that can be reused without duplication.

## Repository Evidence Review

| Existing Surface | Classification | Evidence Role | Recommended Action |
| --- | --- | --- | --- |
| `app/features/breadth/breadth_observation_builder.py` | Runtime Production-shaped | Builds breadth observation payloads from histories and populates evidence/lineage shells | Reuse as the observation producer core |
| `app/features/breadth/breadth_job.py` | Runtime Partial | Orchestrates dry-run breadth observation generation and writer invocation | Reuse for local dry-run orchestration |
| `app/features/breadth/breadth_writer.py` | Runtime Partial | Mock writer validates breadth observations and tracks accepted/rejected rows | Reuse for validation and evidence reporting; do not treat as JSONL builder |
| `app/features/breadth/breadth_validator.py` | Runtime Production-shaped | Validates breadth observation fields and duplicate batch keys | Reuse as validation baseline |
| `app/features/breadth/breadth_report.py` | Runtime Partial | Produces compact dry-run evidence report | Reuse for dry-run evidence summaries |
| `app/normalization/breadth_participation.py` | Runtime Production-shaped | Normalizes fixture-backed breadth participation records | Reuse normalization logic where compatible |
| `app/sources/breadth_participation_sources.py` | Planning-only | Source candidates and next-step planning only | Reuse as discovery context, not as runtime builder |
| `scripts/dry_run_breadth_participation.py` | Dry-run only | Emits dry-run counts, metric types, and universes without writing handoff JSONL | Reuse for dry-run evidence checks |
| `scripts/preflight_breadth_participation_operations.py` | Planning-only | Preflight checks for docs/scripts and expected metric/universe sets | Reuse as planning guardrail only |
| `scripts/plan_breadth_participation_sources.py` | Planning-only | Lists source candidates and next required step | Reuse as planning context only |
| `tests/unit/test_breadth_builder.py` | Tested | Verifies builder behavior and structure | Keep as existing coverage |
| `tests/unit/test_breadth_writer.py` | Tested | Verifies mock writer validation and acceptance behavior | Keep as existing coverage |
| `tests/unit/test_breadth_validator.py` | Tested | Verifies breadth validation behavior | Keep as existing coverage |
| `tests/unit/test_breadth_dry_run_job.py` | Tested | Verifies dry-run orchestration and report generation | Keep as existing coverage |
| `tests/unit/test_breadth_report.py` | Tested | Verifies breadth report shape | Keep as existing coverage |

## What Already Exists In Ingestion?

The repo already has:
- breadth observation building logic
- breadth validation
- dry-run orchestration
- mock writer behavior
- compact dry-run reporting
- planning docs and source candidates

What is not found:
- a dedicated Breadth Observations JSONL handoff builder
- a JSONL handoff artifact writer for breadth observations
- a dedicated ingestion-owned quarantine artifact path for breadth handoff JSONL

## Current Stage Assessment

| Surface | Category | Classification | Evidence | Recommended Action |
| --- | --- | --- | --- | --- |
| `breadth_observation_builder.py` | Acquisition/Normalization | Runtime Production-shaped | Produces canonical breadth observation payloads | Reuse |
| `breadth_job.py` | Dry-run orchestration | Runtime Partial | Builds a single observation row and routes it to mock writer | Reuse |
| `breadth_writer.py` | Writer | Runtime Partial | Mock writer validates and counts accepted/rejected rows | Reuse for dry-run only |
| `breadth_validator.py` | Validation | Runtime Production-shaped | Enforces required fields and duplicate batch-key rejection | Reuse |
| `breadth_report.py` | Evidence | Runtime Partial | Emits a compact dry-run report | Reuse |
| `breadth_participation.py` | Normalizer | Runtime Production-shaped | Normalizes fixture-backed records | Reuse where compatible |
| `breadth_participation_sources.py` | Planning | Planning-only | Source candidate metadata only | Keep deferred |
| `dry_run_breadth_participation.py` | Dry-run | Dry-run only | Emits counts and universe/metric summaries | Reuse for discovery and evidence |
| `preflight_breadth_participation_operations.py` | Validation/Planning | Planning-only | Preflight checks for scripts/docs | Keep deferred |
| `plan_breadth_participation_sources.py` | Planning | Planning-only | Source selection roadmap | Keep deferred |
| JSONL handoff builder | JSONL handoff builder | Not Found | No dedicated breadth JSONL builder found in repository search | Implement next if builder is required |

## Is There Already A Breadth Observations JSONL Handoff Builder?

No, not found.

The repo has runtime-producing breadth observation logic, validation, dry-run orchestration, and reporting, but no dedicated JSONL handoff builder that clearly emits contract-aligned handoff records for the data repo.

## Contract Alignment Review

Existing breadth runtime surfaces partially align with the data-side contract expectations:
- `observation_date` is present in the observation payload.
- `universe` is present, but the canonical contract-facing `universe_key` bridge is not a dedicated ingestion surface.
- `source` exists, but the contract expects explicit lineage fields such as `source_vendor`, `source_dataset`, and `source_sha256`.
- `advancers`, `decliners`, `unchanged`, `advancing_volume`, `declining_volume`, `new_highs`, `new_lows`, and percent-above-MA metrics are present.
- `schema_version`, `metadata`, and deterministic idempotency coverage are not clearly emitted by a dedicated JSONL builder.
- validation and duplicate rejection exist, but quarantine and JSONL artifact generation are not found as a breadth-specific handoff path.

## What Should Not Be Built Here

Do not build or promote:
- universe membership construction
- derived analytics
- breadth thrust
- McClellan oscillator
- A/D line
- sector participation
- sector rotation
- AI/trading signals
- production activation

## Exact Next Recommendation

Implement Breadth Observations JSONL Handoff Builder.

## Production Statement

No vendor call was made, no download occurred, no scheduler was activated, no backfill ran, no production write occurred, and no production rollout is approved.
