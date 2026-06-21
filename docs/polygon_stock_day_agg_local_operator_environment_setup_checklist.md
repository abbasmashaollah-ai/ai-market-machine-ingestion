# Polygon Stock Day Agg Local Operator Environment Setup Checklist

## Purpose

Operator-only checklist to prepare the local environment for a safe vendor listing/probe retry.

## Provenance

- Environment setup readiness documented: `71ee22d`
- Readiness checker: `db50f4f`

## Current Blocker

- `boto3` declared but unavailable in the active environment
- Required Polygon flat-file config keys missing
- `safe_to_retry_probe` false

## Dependency Setup Checklist

- Activate the project virtual environment
- Install dependencies through the repo’s normal local install process
- Do not add new dependency declarations unless needed later
- Do not commit environment or lock changes unless intentionally reviewed

## Config Setup Checklist

- Set these environment variables securely outside git:
  - `POLYGON_API_KEY`
  - `POLYGON_FLAT_FILE_ACCESS_KEY_ID`
  - `POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`
  - `POLYGON_FLAT_FILE_ENDPOINT`
  - `POLYGON_FLAT_FILE_BUCKET`
  - `POLYGON_FLAT_FILE_PREFIX`
- Never paste values into docs
- Never commit `.env` files unless explicitly designed as non-secret templates
- Never print values in terminal logs shared back to ChatGPT/Codex

## Safe PowerShell Command Patterns

- Check variable presence without printing values:

```powershell
@(
  "POLYGON_API_KEY",
  "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
  "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
  "POLYGON_FLAT_FILE_ENDPOINT",
  "POLYGON_FLAT_FILE_BUCKET",
  "POLYGON_FLAT_FILE_PREFIX"
) | ForEach-Object { [bool](Get-Item "Env:$_" -ErrorAction SilentlyContinue) }
```

- Readiness checker command:

```powershell
python scripts/check_polygon_stock_day_agg_probe_environment_readiness.py
```

- Expected readiness success shape:
  - `readiness_passed true`
  - `safe_to_retry_probe true`
  - `vendor_call_attempted false`
  - `remote_listing_attempted false`
  - `download_attempted false`
  - `file_write_attempted false`
  - `secrets_printed false`

## Safe Continuation Rule

- Only retry vendor listing/probe after `readiness_passed` true and `safe_to_retry_probe` true
- Vendor probe retry must still be listing/probe-only
- No download/quarantine write/parse/normalization/handoff
- Separate approval required before any download

## Not Authorized

- Vendor call/listing/probe by this checklist
- Download
- Quarantine write
- Parse/normalization
- Handoff/intake generation
- Scheduler/backfill
- DB write
- Data repo mutation
- Production staging load
- Canonical promotion
- AI wiring
- Generated output commit
- Unrelated untracked file staging/deletion
- Secrets printed

## Completion Statement

This checklist records the operator steps needed before any future safe vendor probe retry.
