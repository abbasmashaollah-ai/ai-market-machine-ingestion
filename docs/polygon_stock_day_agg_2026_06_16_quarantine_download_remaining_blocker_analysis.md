# Polygon Stock Day Agg 2026-06-16 Quarantine Download Remaining Blocker Analysis

## Purpose

Explain why the approved `2026-06-16` quarantine download still blocks and define the smallest safe next implementation step.

## Evidence Basis

- Download implementation commit: `a02548b`
- Download approval package commit: `f03976a`
- Operator approval record commit: `3841b8f`
- Manual probe evidence commit: `89ca6da`
- Latest blocker evidence commit: `6fbc6e8`

## Exact Blocker Cause

The approved stock-day-specific wrapper is in place, but the executed download attempt still blocked because the active execution environment reported missing Polygon flat-file configuration:

- `config_classification: "missing"`
- `credentials_present: false`
- `download_attempted: false`
- `local_file_exists: false`
- `local_file_size_bytes: 0`
- `remote_listing_error_code_redacted: "client_error"`
- `remote_listing_error_message_redacted: "remote listing failed safely"`

That means the blocker is not the approval phrase or the wrapper date gate. The blocker is the environment/config side of the generic downloader path: the code reaches the remote-listing preflight, but the active process lacks the required Polygon flat-file credential/config presence and the remote-listing step fails safely before any quarantine write.

## Where the Blocker Lives

- Wrapper: not the blocker, because it correctly forwards the stock-day-specific approval phrase and date.
- Generic downloader: not the direct blocker, because it now accepts an injected required approval phrase.
- Adapter/environment: the remaining blocker, because it requires Polygon flat-file configuration to be present before a quarantine download can proceed.
- Safety policy: intentionally still blocks unsafe download execution when config is missing.

## Smallest Safe Fix Plan

The smallest safe next step is not to weaken the code path. It is to ensure the operator execution environment has the required Polygon flat-file configuration loaded before rerunning the approved command.

Keep all of the following unchanged:

- one-date only
- exact approved phrase
- exact output path
- no parse
- no normalization
- no handoff/intake
- no DB write
- no data repo mutation
- no scheduler/backfill
- no AI wiring
- no secrets printed

## Required Tests For the Fix

If a code change becomes necessary later, the tests should remain focused and mocked:

- mocked remote object read/download path
- wrong phrase blocks
- missing phrase blocks
- correct phrase allows one-date quarantine write under mock
- output path exactly correct
- no parse/normalization/handoff/intake/DB/data repo/scheduler/backfill/AI flags

## Next Command Recommendation

Implement the smallest safe fix only if the environment is not already correctly configured, then rerun the targeted tests, and after that execute the approved one-date download and record evidence.

## Not Authorized

- Live vendor call/listing/probe
- Remote file read
- Download
- Quarantine write
- Parse/normalization/handoff/intake
- DB write
- Data repo mutation
- Scheduler/backfill
- AI wiring
- Generated output commit
- Unrelated untracked file staging/deletion
- Secrets printed

## Completion Statement

This analysis records that the remaining blocker is environment/config presence for the download path, not the stock-day approval phrase or wrapper date gate.
