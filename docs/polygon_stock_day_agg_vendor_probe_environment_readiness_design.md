# Polygon Stock Day Agg Vendor Probe Environment Readiness Design

## Purpose

Define environment requirements before retrying Polygon stock day aggregate vendor listing/probe.

## Current Blocker

- Blocker evidence commit: `e16402c`
- Probe utility exists
- Safe-block behavior worked
- Remote listing was not executed
- Missing Polygon flat-file config
- Missing `boto3` dependency

## Required Environment Readiness

- Required non-secret config keys/names must be present
- Required AWS/S3/Polygon flat-file credential/config presence must be verified without exposing secrets
- `boto3` dependency must be available
- Command must remain listing/probe-only
- No download
- No file write
- No quarantine write
- No parse/normalization/handoff

## Secret Handling

- Do not print credentials
- Do not commit credentials
- Do not include DB URLs
- Do not store API keys, tokens, or passwords in docs
- Only document presence or absence of required config by key name, never values

## Safe Retry Criteria

- `boto3` available
- Required config present
- Operator approval record already exists
- Probe command uses listing-only mode
- Output/evidence captures availability and metadata only
- No download flags used

## Retry Command Pattern

Use the existing metadata-only preflight command pattern with the same listing-only intent:

`python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1`

Do not add download, write, parse, or handoff flags.

## Failure Behavior

- If config or dependency is still missing, block again and record evidence
- If vendor denies access, record availability/access evidence but do not retry with broader permissions
- If multiple files are found, do not download; create a separate download approval package

## Next Step

Create an environment readiness approval/check package or run a safe dependency/config presence check. Do not retry vendor listing until environment readiness is documented.

## Safety Boundary

- No vendor call/listing/probe in this design
- No download
- No package install
- No code/script modification
- No scheduler/backfill
- No DB write
- No data repo mutation
- No AI wiring
- No generated output commit
- Unrelated untracked files untouched
- No secrets or DB URLs

## Completion Statement

This design records the environment prerequisites required before a future safe retry of the Polygon stock day aggregate vendor probe.
