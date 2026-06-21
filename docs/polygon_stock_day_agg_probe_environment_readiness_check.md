# Polygon Stock Day Agg Probe Environment Readiness Check

## Purpose

Document the local readiness check required before retrying Polygon stock day aggregate vendor listing/probe.

## What This Check Does

- Verifies only dependency and config presence
- Does not call vendors
- Does not list vendor files
- Does not download vendor files
- Does not write files
- Does not create handoff outputs
- Does not create intake packages
- Does not print secrets or DB URLs

## Checked Config Key Names

- `POLYGON_API_KEY`
- `POLYGON_FLAT_FILE_ACCESS_KEY_ID`
- `POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`
- `POLYGON_FLAT_FILE_ENDPOINT`
- `POLYGON_FLAT_FILE_BUCKET`
- `POLYGON_FLAT_FILE_PREFIX`

## Dependency Check

- `boto3` availability
- Only safe type-level error reporting if import fails

## Safe Retry Criteria

- `boto3` available
- Required config keys present
- Operator approval record already exists
- Probe command remains listing-only
- No download flags are used

## Next Step If Readiness Passes

Retry vendor listing/probe only.

## Next Step If Readiness Fails

Configure the missing dependency or config outside the repository, then rerun the readiness check.

## Safety Boundary

- No scheduler activation
- No backfill
- No DB write
- No data repo mutation
- No AI wiring
- Unrelated untracked files untouched
- No secrets or DB URLs

## Completion Statement

This check package documents the presence/absence requirements needed before any future safe vendor probe retry.
