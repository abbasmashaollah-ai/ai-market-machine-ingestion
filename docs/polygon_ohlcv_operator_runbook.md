# Polygon OHLCV Operator Runbook

`scripts/generate_polygon_ohlcv_operator_runbook.py` prints an ordered manual runbook for a small Polygon OHLCV cycle.

## Scope

The generator is read-only. It does not execute commands, call Polygon, or write to the database.

The runbook includes:

1. the preflight command
2. the recommendation verifier command
3. the recommended per-symbol manual command from preflight
4. optional per-symbol evidence-chain verification commands

## Safety

The generated commands never include secrets and never include `--confirm-write` by default.

`ai-market-machine-data` remains the schema owner.
