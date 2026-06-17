# Polygon Stock Day Agg Local Handoff Artifact Validator

This validator checks only generated local handoff artifacts.

It reads a local batch manifest, follows the manifest to per-date summary JSON and rows JSONL files, and verifies the artifacts are internally consistent.

It does not:

- call vendor APIs
- download remote files
- write to a database
- activate ingestion
- activate schedulers
- mutate production

Checks performed:

- manifest exists and parses
- summary JSON files exist and parse
- rows JSONL files exist and parse
- row counts match across manifest, summaries, and rows files
- each row contains the required handoff fields
- dataset and source metadata match the expected contract
- trade dates stay within the manifest date range
- safety flags remain non-production

The validator is a local quality gate before any later data-repo acceptance step.
That later ingestion step remains separate and is not enabled here.
