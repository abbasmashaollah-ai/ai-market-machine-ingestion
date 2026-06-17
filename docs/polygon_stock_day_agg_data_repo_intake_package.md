# Polygon Stock Day Agg Data Repo Intake Package

This builder creates a compact local-only descriptor for a later `ai-market-machine-data` intake step.

It does not copy the rows JSONL file, and it does not write to the data repo.

It reads the validated local handoff manifest, confirms the local handoff artifacts are valid, and emits a small descriptor JSON that a later process can consume.

It does not:

- call vendor APIs
- download remote files
- write to a database
- activate ingestion
- activate schedulers
- mutate production
- mutate `ai-market-machine-data`

The descriptor contains:

- package identity
- dataset and source metadata
- manifest path and hash
- artifact root
- per-date summary and rows paths
- row counts
- safety and approval metadata

This is a staging descriptor only.
The later `ai-market-machine-data` consumer remains a separate step and is not enabled here.
