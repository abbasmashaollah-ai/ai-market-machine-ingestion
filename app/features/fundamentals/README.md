# fundamentals

Dry-run fundamentals evidence slice.

This package converts fixture company financial snapshots into deterministic fundamental observations and reports.

It is evidence-only:
- no AI decision
- no trading signal
- no vendor calls
- no database writes

## Current Contract

Supported observation/report fields include:
- `source_attribution`
- `dataset_version`
- `created_at`
- `updated_at`

Defaults are deterministic and remain dry-run only:
- `dataset_version` defaults to `fundamentals_dry_run_v1`
- `created_at` and `updated_at` are derived from the observation date when not supplied
- no DB writes
- no vendor calls
- no scheduler activation
- no AI/judge/capital/trading decisions
