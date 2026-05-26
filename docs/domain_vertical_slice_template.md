# Domain Vertical Slice Template

Use this template when adding a new ingestion domain to `ai-market-machine-ingestion`.

## Domain purpose

Describe the market-data domain and the operator use case it serves.

## Data repo dependency

State the data-side schema, contract, or read-model dependency that must already exist in `ai-market-machine-data`.

## Ingestion repo responsibilities

List the producer-side responsibilities that belong in `ai-market-machine-ingestion`:

- vendor adapter
- normalization contract
- validation and quality checks
- writer/store boundary
- run-history recording
- quality-result recording
- lineage recording
- checkpoint handling when applicable

## Vendor adapter

Describe the vendor adapter entrypoint and the minimal surface it needs to expose.

## Normalization contract

Describe the normalized record shape and the target canonical model contract.

## Validation and quality checks

Describe the required validation checks, safe failure behavior, and any quality gating.

## Writer/store boundary

Describe which module owns writes and which stores or writers are allowed to persist data.

## Run-history recording

Describe when run history is recorded and which flags or modes enable it.

## Quality-result recording

Describe when quality results are recorded and how they are represented.

## Lineage recording

Describe when lineage rows are recorded and what evidence payload they contain.

## Preflight command

Describe the read-only preflight or readiness command for the domain.

## Runner command

Describe the manual operator runner command and its default execution mode.

## Evidence verifier

Describe the read-only evidence verification command for the domain.

## Required docs

List the docs that must exist for the domain slice:

- manual runner doc
- preflight doc
- evidence verifier doc
- scheduler readiness or contract doc if the domain is scheduler-facing

## Required tests

List the tests that must exist for the domain slice:

- writer contract tests
- boundary guardrail tests
- preflight tests
- runner tests
- evidence verifier tests

## Forbidden imports and logic

The new domain slice must not introduce:

- FastAPI routes
- Alembic or schema ownership
- AI, trading, risk, signal, regime, or portfolio logic
- direct data-repo internal imports
- scheduler activation

## Commit and push checklist

- confirm the manual command inventory includes the new modules
- run focused unit tests
- run `git diff --check`
- run `git status`
- commit only the intended files
- push the branch after verification
