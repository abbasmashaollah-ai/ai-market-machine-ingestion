# FRED Macro Live Dry Run

The live dry-run path fetches FRED observations and normalizes them without writing to storage.

Boundary:
- no DB writes
- no scheduler
- no AI/trading/risk/signal/regime logic
- API key is only required for `--live-check`
- live dry-runs use the newest observations first when `--max-observations` is set

Supported starter series:
- DGS10
- DGS2
- FEDFUNDS
- CPIAUCSL
- UNRATE
