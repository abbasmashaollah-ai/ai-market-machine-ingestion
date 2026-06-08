# Market Feature Bundle Multi-Symbol Production Seed Command

## Purpose

- provide a dedicated multi-symbol production seed command scaffold for QQQ/IWM/DIA
- keep dry-run/no-write mode as the default

## Command behavior

- default mode is dry-run/no-write
- default dry-run/no-write mode
- guarded `--execute` branch exists for the symbol-agnostic writer contract
- guarded --execute branch exists for the symbol-agnostic writer contract
- accepts `--symbols QQQ,IWM,DIA`
- accepts `--observation-date 2026-01-15`
- accepts `--dataset-version production_pilot.v1`
- accepts `--output-file` as an optional local summary path
- production write requires `--execute` plus explicit approval and DB URL env vars
- tests use injected fake writer only
- target symbols are restricted to QQQ/IWM/DIA
- fixture payloads are used as source inputs
- safe JSON summary is emitted

## Safety boundaries

- no scheduler activation
- no broad backfill
- no automated recurring job
- no AI Machine runtime wiring
- no DB writes in tests
- no vendor calls
- no live API calls
- no secrets printed

## Output contract

- `dry_run`
- `execute_requested`
- `db_write_attempted`
- `db_write_allowed`
- `approval_env_present`
- `db_url_env_present`
- `symbols_requested`
- `symbols_ready`
- `symbols_blocked`
- `per_symbol_status`
- validation gates
- `symbols_written`
- `symbols_noop`
- `symbols_conflict`
- `symbols_failed`
- `per_symbol_write_status`
- `verification_status`
- `idempotency_key_prefix` only
- idempotency_key_prefix only
- `next_step`
- local `output-file` only
- output-file local only

## Production write stance

- production write currently blocked unless implementation is explicitly approved
- production write requires explicit second approval before DB write
- production execution still requires user-run command and verification
- data api verification still required after any future write
