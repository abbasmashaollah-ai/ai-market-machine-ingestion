# OHLCV Scheduler Readiness

`scripts.assess_ohlcv_scheduler_readiness.py` is a read-only assessment script. It does not start a scheduler and it does not change Railway startup behavior.

## What it checks

- the manual OHLCV command inventory is complete
- FMP preflight exists and runs in dry-run/preflight mode
- Polygon preflight exists and runs in dry-run/preflight mode
- evidence-verifier scripts exist
- writer-contract tests exist
- boundary-guardrail tests exist
- manual docs exist
- no active scheduler entrypoint exists yet
- Railway does not point at a scheduler startup command
- required env expectations are documented

## Expected environment

- `DATABASE_URL` is only required for write/evidence-recording paths and any preflight path that explicitly requests existing-data checks
- `FMP_API_KEY` is only required for confirm-write or live-check paths
- `POLYGON_API_KEY` is only required for confirm-write or live-check paths
- the writer contract and boundary guardrail tests are expected to remain in the repo as the main guardrails for manual OHLCV operations

## Status output

The script prints:

- `scheduler_readiness_status=PASS|WARN|FAIL`
- `readiness_score=<integer>`
- a checklist summary
- `blockers=...`
- `warnings=...`
- `next_required_step=...`

## Interpretation

- `PASS` means the manual foundation is present and no active scheduler activation path exists.
- `WARN` means the manual foundation is present but optional docs or helper artifacts are missing.
- `FAIL` means a blocker exists, such as:
  - incomplete manual command inventory
  - forbidden imports in manual command paths
  - active scheduler activation files
  - Railway startup pointing at a scheduler command

This repository remains producer-free. Scheduler readiness is only an assessment layer over the manual OHLCV command set.
