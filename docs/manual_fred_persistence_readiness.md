# Manual FRED Persistence Readiness

`scripts/check_manual_fred_persistence_readiness.py` is a read-only operator diagnostic for incremental FRED persistence readiness.

## Scope

The script:

- checks whether `FRED_API_KEY` is present
- checks whether `DATABASE_URL` is present
- validates `DATABASE_URL` syntax using existing safe config validation only
- imports the manual ingestion command modules safely
- prints a read-only readiness summary

## Output

The script prints:

- `dry_run_ready`
- `confirmed_write_ready`
- `missing`
- `imported`

## Safety

The script does not:

- call FRED
- connect to a database
- write to a database
- schedule work
- run automatically on Railway startup

`ai-market-machine-data` remains the schema owner.

## Verification Log

- `dry_run_ready=true`
- `confirmed_write_ready=false`
- `missing=['DATABASE_URL']`
- imported manual command modules successfully
