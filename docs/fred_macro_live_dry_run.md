# FRED Macro Live Dry Run

The live dry-run path fetches FRED observations and normalizes them without writing to storage.

Boundary:
- no DB writes in dry-run mode
- no scheduler
- no AI/trading/risk/signal/regime logic
- API key is only required for `--live-check`
- live dry-runs use the newest observations first when `--max-observations` is set
- confirmed writes require `--live-check`, `--confirm-write`, `DATABASE_URL`, and `FredMacroWriter`
- `write_status` is `DRY_RUN`, `WRITTEN`, `SKIPPED`, `NO_EFFECT`, or `FAILED`
- `no_db_writes=False` when confirmed write is attempted

Supported starter series:
- DGS10
- DGS2
- FEDFUNDS
- CPIAUCSL
- UNRATE
