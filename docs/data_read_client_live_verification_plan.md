# Data Read Client Live Verification Plan

## Purpose

This document defines the read-only live verification plan for `DataReadClient` against `ai-market-machine-data`.

The code path is mocked and unit-tested today. This plan describes the safe, human-approved steps needed before any runtime live read is allowed.

## Current Implementation Status

- `DataReadClient` exists in `app/clients/data_read_client.py`
- it is covered by mocked unit tests only
- no live endpoint verification has been done
- no write path is involved

## Required Environment Variables

- `AI_MARKET_MACHINE_DATA_BASE_URL`
- `OPS_INTERNAL_TOKEN`

## Auth Header

- `X-Ops-Internal-Token`

The token must never be logged or printed.

## OpenAPI Verification Step

Before any live read command is executed, fetch:

```text
GET {AI_MARKET_MACHINE_DATA_BASE_URL}/openapi.json
```

Use the OpenAPI document to confirm the private-read route shape and request/response contract.

## Expected Private-Read Endpoint Discovery

The verification step should identify the certified OHLCV private-read endpoint exposed by `ai-market-machine-data`.

The exact route is intentionally left uncalled here until the OpenAPI document confirms it.

## Read-Only Command Examples

Use token placeholders only:

```bash
python -m scripts.example_data_read_client_check --base-url "$AI_MARKET_MACHINE_DATA_BASE_URL" --token "<OPS_INTERNAL_TOKEN>"
```

Any live verification command must remain read-only and must not write to the database.

## Expected Successful Response Shapes

The live client should accept any of the following response envelopes:

- list
- `{"rows": [...]}`
- `{"data": [...]}`
- `{"ohlcv": [...]}`
- `{"historical": [...]}`
- `{"results": [...]}`

## Failure Handling

The live verification plan should explicitly test or confirm the following outcomes:

- `401` / `403` auth failures
- `404` endpoint missing
- `500` server error
- empty response
- invalid response shape

## Safety Rules

- no vendor calls
- no DB writes
- no POST/PUT/PATCH/DELETE
- no scheduler activation
- no AI Machine changes
- no token logging

## Approval Gate Before Runtime

Human approval is required before any live read command is executed.

This plan is documentation for that approval gate, not authorization to run the command.

Human approval must happen before any live verification step is executed.

human approval
