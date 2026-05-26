# FRED Macro Evidence Chain

This verifier reads the approved `macro_rate_observations` table only.

It reports:
- `series_count`
- `total_rows`
- `row_count_by_series`
- `latest_observation_dates`
- `missing_series`
- `missing_value_count`
- `evidence_status`

Status rules:
- `PASS` when all requested series have at least one row
- `WARN` when rows exist but some requested series are missing
- `FAIL` when no rows exist or the required DB read fails

The verifier is read-only and does not call vendors or write data.
It uses the FRED starter series by default and supports repeated `--series` flags for explicit checks.
