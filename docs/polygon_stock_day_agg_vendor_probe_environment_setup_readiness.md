# Polygon Stock Day Agg Vendor Probe Environment Setup Readiness

## Purpose

Prepare the environment for a safe Polygon stock day aggregate vendor listing/probe retry.

## Current Blocker

- Blocker evidence commit: `e16402c`
- `boto3` unavailable
- Required Polygon flat-file config keys missing
- `readiness_passed` false
- `safe_to_retry_probe` false

## Required Dependency

- `boto3`
- Dependency declaration status: already present in `pyproject.toml`

## Required Config Key Names

- `POLYGON_API_KEY`
- `POLYGON_FLAT_FILE_ACCESS_KEY_ID`
- `POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`
- `POLYGON_FLAT_FILE_ENDPOINT`
- `POLYGON_FLAT_FILE_BUCKET`
- `POLYGON_FLAT_FILE_PREFIX`

## Secret Handling

- No secrets in docs
- No secrets in git
- No DB URLs
- No token values
- No command output containing secret values

## Operator Setup Instructions

- Install dependencies through the project’s normal local process
- Set required environment variables securely outside git
- Rerun `python scripts/check_polygon_stock_day_agg_probe_environment_readiness.py`

## Safe Continuation Rule

- Only retry vendor listing/probe if `readiness_passed` is true and `safe_to_retry_probe` is true
- Still no download
- Still no quarantine write
- Still no parse/normalization/handoff
- Still no DB/data repo/scheduler/backfill/AI

## Not Authorized

- Package installation by Codex
- Vendor call/listing/probe
- Download
- File write to `outputs/quarantine`
- Parse/normalization
- Handoff/intake generation
- DB write
- Data repo mutation
- Scheduler/backfill
- AI wiring
- Generated output commit
- Unrelated untracked file staging/deletion
- Secrets printed

## Completion Statement

This document records the setup requirements needed before any future safe vendor probe retry.
