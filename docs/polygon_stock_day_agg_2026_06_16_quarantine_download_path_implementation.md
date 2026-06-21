# Polygon Stock Day Agg 2026-06-16 Quarantine Download Path Implementation

## Purpose

Repair the safe one-date quarantine download path for the approved `2026-06-16` Polygon stock day aggregate file.

## Blocker Cause Found

- Blocker commit: `0c7ae7a`
- Approval package commit: `f03976a`
- Operator approval record commit: `3841b8f`
- Manual probe evidence commit: `89ca6da`
- The guarded downloader was hard-wired to the generic approval phrase `APPROVE POLYGON FLAT FILE SINGLE DATE LOCAL QUARANTINE DOWNLOAD`
- The approved stock-day phrase `APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD` did not match, so the utility blocked safely before any quarantine write

## What Was Implemented

- Added a stock-day-specific wrapper script: `scripts/download_polygon_stock_day_agg_single_date_quarantine.py`
- Added support in the generic downloader for an injected required approval phrase without weakening the existing generic safety behavior
- Enforced one-date-only behavior for `2026-06-16`
- Kept the output path fixed to `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz` for the approved date
- Preserved the no-parse, no-normalization, no-handoff, no-intake, no-DB, no-scheduler, and no-AI guarantees

## Future Approved Command

`python scripts/download_polygon_stock_day_agg_single_date_quarantine.py --date 2026-06-16 --approve-local-quarantine-download --approval-phrase "APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD" --quarantine-dir outputs/quarantine/polygon_flat_files`

## Safety Guarantees

- One file only
- One date only
- No remote file read beyond the approved quarantine download flow
- No parse
- No normalization
- No handoff candidate generation
- No intake package generation
- No DB write
- No data repo mutation
- No scheduler activation
- No backfill
- No AI wiring
- No generated output commit
- No secrets or DB URLs are printed
- Unrelated untracked files remain untouched

## Execution Statement

No live download was executed by this implementation step.

## Next Step

The next step is live one-date quarantine download execution evidence for `2026-06-16` using the approved stock-day-specific command above.
