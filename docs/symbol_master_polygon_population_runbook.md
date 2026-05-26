# Symbol Master Polygon Population Runbook

This runbook describes a staged, controlled operator path for populating `public.symbol_master` from Polygon.

## Sequence

1. Preflight the manual workflow
   - `scripts/preflight_symbol_master_operations.py`
2. Run the sample dry-run
   - `scripts/dry_run_polygon_symbol_master.py`
3. Run the live-check dry-run
   - `scripts/dry_run_polygon_symbol_master.py --live-check --limit 25 --max-records 1000`
4. Write a small confirmed batch
   - `scripts/dry_run_polygon_symbol_master.py --live-check --confirm-write --limit 25 --max-records 1000`
5. Assess coverage and reconciliation
   - `scripts/assess_symbol_master_coverage.py --vendor polygon --min-total 1 --min-active 1`
6. Verify evidence
   - `scripts/verify_symbol_master_evidence_chain.py`

## Recommended thresholds

- `--limit 25`
- `--max-records 1000`
- `--min-total 1`
- `--min-active 1`
- `--max-missing-exchange-ratio 0.05`
- `--max-missing-asset-type-ratio 0.05`

## Rollback and retry notes

- Confirmed writes are limited to the approved `SymbolMasterWriter` path.
- If a batch is too large or coverage is weak, stop and rerun with smaller limits.
- If a confirmed write was accepted but the coverage assessment or evidence verifier reports WARN/FAIL, do not expand the batch. Re-run coverage, inspect the affected rows, and verify evidence before retrying.

## What not to do

- Do not run scheduler paths.
- Do not add FastAPI routes.
- Do not add migrations.
- Do not claim schema ownership.
- Do not run confirmed writes without `--live-check`.
- Do not expand batches without checking coverage and evidence.
- Do not use the plan command to write data.

## Escalation

If `coverage_status` is `WARN` or `FAIL`, pause confirmed writes, rerun the coverage assessment with the relevant filters, and review the evidence verifier output before proceeding.

## Boundary

This runbook is advisory only. It does not create new write paths. It references existing read-only and confirmed-write commands only.
