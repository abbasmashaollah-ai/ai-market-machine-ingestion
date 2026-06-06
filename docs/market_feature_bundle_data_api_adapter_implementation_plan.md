# Market Feature Bundle Data API Adapter Implementation Plan

## Purpose

- define how to implement the read-only Data API adapter safely
- keep the first implementation shadow-only
- do not alter AI Machine reasoning behavior
- do not remove legacy data files yet

This plan is limited to adapter design and tests. It does not authorize runtime wiring into production paths.

## Adapter Target

- `app/clients/data_read_client.py`
- route `GET /internal/read/market-feature-bundle/{universe}`
- first universe `SPY`
- token from environment variable only
- base URL from environment variable only
- no DB URL
- no database imports
- no vendor imports
- no writes

The adapter is a read-only boundary to certified evidence.

## Adapter Responsibilities

- build route URL
- send GET request
- include internal auth token header
- parse JSON response
- validate status code
- enforce consumption gates:
  - `certification_status CERTIFIED`
  - `validation_status PASS`
  - `coverage_status COMPLETE`
  - `quality_status PASS`
  - `missing_data_evidence empty`
  - `stale_data_evidence empty`
  - `supported schema_version`
- return a typed or structured evidence object, or a safe no-evidence result
- redact token and URL in errors and logs
- expose `idempotency_key_prefix` only

The adapter should only surface evidence, metadata, and gate outcomes.

## Adapter Non-Responsibilities

- no judge posture
- no trading decision
- no risk posture
- no portfolio allocation
- no capital logic
- no execution logic
- no scheduler/backfill
- no production writes
- no vendor fetch
- no raw data normalization

These remain AI Machine reasoning concerns or ingestion/data ownership concerns, not adapter concerns.

## Error Behavior

- `401`/`403` -> unauthorized no-evidence result
- `404` or missing row -> no-evidence result
- `500` -> route failure no-evidence result
- timeout -> no-evidence result
- malformed JSON -> no-evidence result
- uncertified, invalid, or stale -> gated no-evidence result
- never infer negative market state from missing/no-evidence

Errors must be safe by default and must not be converted into market judgments.

## Shadow-Mode Integration Boundary

- first consumer: `app/features/sector_rotation/sector_rotation_reader.py`
- replace only input-fetch/data-loading portion
- keep sector rotation calculations unchanged
- compare API evidence shape to legacy/local input
- log differences only
- no changes to decisions
- no capital impact
- no portfolio changes
- no user-facing recommendation

This is the cleanest boundary for a shadow-only migration because it isolates input acquisition from the downstream deterministic calculations.

## Test Plan

- adapter tests with mocked successful response
- `401/403 mocked tests`
- `500 mocked test`
- timeout mocked test
- malformed JSON mocked test
- missing row mocked test
- uncertified response mocked test
- validation failure mocked test
- stale evidence mocked test
- no vendor import/source scan
- no DB import/source scan
- no secret logging/source scan
- AI reasoning boundary test proving key feature logic files are not modified

Tests should prove both the adapter contract and the preservation of AI Machine reasoning modules.

## Configuration

- `AI_MARKET_MACHINE_DATA_BASE_URL`
- `AI_MARKET_MACHINE_DATA_INTERNAL_TOKEN`
- optional timeout variable
- all optional defaults safe
- missing config returns disabled/no-evidence result, not crash

Configuration should fail closed for consumption and open only for safe no-evidence behavior.

## First Implementation Sequence

1. add tests first
2. add or extend adapter
3. do not wire into production path yet
4. add shadow-mode helper behind explicit flag
5. run mocked tests only
6. then plan one local manual route check
7. then plan shadow comparison

This sequence prevents accidental runtime behavior changes before test coverage exists.

## Approval Gates

- implementation plan approved
- tests approved
- no runtime route wiring without approval
- no AI Machine decision behavior changes
- no legacy deletion without approval

No production activation should happen until the plan and tests are explicitly approved.
