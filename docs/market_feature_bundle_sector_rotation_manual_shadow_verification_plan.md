# Market Feature Bundle Sector Rotation Manual Shadow Verification Plan

## Purpose

- manual shadow verification
- define how to manually verify the sector rotation shadow helper
- shadow comparison only
- Data API remains non-authoritative
- no AI Machine behavior changes

This plan covers manual verification and does not authorize a live shadow check yet.

## Current State

- shadow helper exists
- disabled by default
- baseline tests passed
- shadow tests passed
- primary sector rotation output unchanged when disabled
- no production changes

The current state is safe for documentation-only verification planning.

## Required Env / Config For Later Manual Check

- `AI_MARKET_MACHINE_DATA_BASE_URL`
- `AI_MARKET_MACHINE_DATA_INTERNAL_TOKEN`
- optional timeout variable
- token must not be printed
- base URL may be redacted in logs
- no DB URL

Environment values should be treated as secrets and handled with redaction.

## Manual Check Scope

- first universe `SPY`
- route `GET /internal/read/market-feature-bundle/{universe}`
- `certified_only` behavior
- `production_pilot.v1` expected if using the current preserved row
- no writes
- no vendor calls
- no scheduler/backfill

The manual check should stay in read-only shadow mode and should not activate any write or scheduler behavior.

## Expected Shadow Behavior

- fetch legacy/local sector rotation input as usual
- fetch data API evidence only when explicit shadow flag enabled
- compare `evidence_available`
- compare `dataset_version`
- compare `schema_version`
- compare `certification_status`
- compare `validation_status`
- compare `coverage_status`
- compare `quality_status`
- compare `observation_date` / `generated_at` if present
- compare section availability and warnings if present
- report differences only
- no changes to primary output

If the shadow flag is disabled, the existing output should remain unchanged.

## Failure Handling

- missing config -> skip shadow
- `401/403` -> unauthorized no-evidence
- `500` -> route failure no-evidence
- timeout -> no-evidence
- uncertified / invalid / incomplete response -> gated no-evidence
- no negative market inference from no-evidence

Failure conditions must not be interpreted as bearish or bullish market evidence.

## Boundaries

- no judge posture changes
- no trading decision changes
- no risk posture changes
- no portfolio allocation changes
- no capital logic changes
- no execution logic
- no production writes
- no DB access
- no vendor fetch
- no full idempotency_key
- no token/DB URL logging

These boundaries preserve AI Machine reasoning and keep the manual check non-authoritative.

## Verification Checklist

- run baseline sector rotation test before manual check
- run shadow helper unit tests before manual check
- confirm env vars set without printing values
- run manual shadow diagnostic script only after a script is approved
- inspect diagnostic output for redaction
- clear env vars after check
- record result in checkpoint if successful

The checklist is intentionally conservative so the manual check remains auditable and reversible.

## Next Implementation After This Plan

- create a manual shadow diagnostic script
- tests must mock Data API
- automated tests must mock Data API
- script must be opt-in only
- script must never alter AI Machine outputs
- script must not call live route in automated tests

The next step is a dedicated manual diagnostic utility, not runtime integration.
