# HTTP Transport

The shared HTTP transport layer in `app/vendors/common/http.py` provides a small urllib-based transport and metadata contracts.

## Scope

This layer provides:

- request metadata
- response metadata
- HTTP response containers with text and optional JSON
- a concrete standard-library transport
- query parameter support
- timeout handling
- error mapping into vendor-common exceptions

## Boundary

This layer does not:

- call vendor-specific endpoints directly
- execute ingestion pipelines
- write to the database
- implement writers
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- The transport uses the Python standard library `urllib`.
- JSON parsing is opportunistic; raw text remains available when JSON decoding fails.
- `HttpResponse` exposes convenience properties for `status_code`, `raw_text_length`, and `parsed_json` while preserving the underlying metadata and raw text.
- Tests should mock transport behavior and avoid live network traffic.
