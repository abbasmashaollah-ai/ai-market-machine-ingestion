# Market Feature Bundle Multi-Symbol Dry-Run Command

## Purpose

- provide a dry-run-only multi-symbol command for QQQ/IWM/DIA
- keep the workflow local-file-only before any production seed/write

## Command behavior

- dry-run only
- default symbols are QQQ, IWM, DIA
- accepts `--symbols QQQ,IWM,DIA`
- accepts `--observation-date 2026-01-15`
- accepts `--output-file` as an optional local file path
- loads fixture payloads only from `tests/fixtures/market_feature_bundle`
- validates each fixture with `tests/fixtures/market_feature_bundle/fixture_validator.py`
- writes local JSON summary only when `--output-file` is provided

## Safety boundaries

- no DB writes
- no production seed/write
- no vendor calls
- no live API calls
- no scheduler activation
- no AI Machine runtime wiring
- no secrets printed

## Output contract

- `dry_run`
- `db_write_attempted`
- `production_write_attempted`
- `vendor_call_attempted`
- `live_api_call_attempted`
- `scheduler_activation_attempted`
- `symbols_requested`
- `symbols_succeeded`
- `symbols_failed`
- `per_symbol_status`
- `validation_status`
- `coverage_status`
- `quality_status`
- `certification_status`
- `dataset_version`
- `schema_version`
- `idempotency_key_prefix` only
- idempotency_key_prefix only
- local `output-file` only
- output-file local only

## Existing blocker

- the existing SPY-only dry-run runner remains SPY-only
- existing SPY-only dry-run blocker
- this command is the dry-run-only multi-symbol path requested before any second approval
- second explicit approval is still required before any DB write
- second explicit approval required before DB write
