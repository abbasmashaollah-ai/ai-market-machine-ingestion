# Options Day Aggregates Sample Handoff

## Purpose

This milestone adds a local sample handoff builder for Massive/Polygon options day aggregates. It converts the verified quarantine file into a capped JSONL sample artifact for inspection and downstream prototype work, without touching production export, ingestion, or database paths.

## Repo/System Review Summary

- The options domain is isolated under `app/vendor_flat_files/options/`.
- The parser and normalizer already exist and were verified against the real inspected quarantine file.
- The sample handoff step belongs after parser/normalizer verification and before any broader downstream sample artifact work.
- This remains separate from the sector ETF stock pipeline and its guarded download/manifest flow.

## Input File Facts

- Input file: `outputs/quarantine/options_flat_files/massive_options_day_aggs_2025-11-05.csv.gz`
- Size: `3531068`
- SHA256: `fbdcf39f693a96251062cb4827ea64c5e5fb9ba44ceb8d0005afbc036d03fb7f`
- Row count: `302354`
- Header columns:
  - `ticker`
  - `volume`
  - `open`
  - `close`
  - `high`
  - `low`
  - `window_start`
  - `transactions`

## Parser / Normalizer Dependency

The handoff builder depends on:

- `app/vendor_flat_files/options/options_day_aggs_parser.py`
- `app/vendor_flat_files/options/options_day_aggs_normalizer.py`

The builder uses their verified local-only behavior and does not introduce any vendor access.

## Sample Handoff Contract

The builder writes a capped JSONL sample artifact from normalized records.

Defaults:

- input: `outputs/quarantine/options_flat_files/massive_options_day_aggs_2025-11-05.csv.gz`
- output: `outputs/handoff/options_day_aggs/options_day_aggs_2025-11-05_sample.jsonl`
- sample limit: `100`
- sample limit max: `1000`

Each JSONL record includes the normalized fields and row-level warnings, with deterministic serialization.

## Output Artifact Path

`outputs/handoff/options_day_aggs/options_day_aggs_2025-11-05_sample.jsonl`

## Approval / Safety Boundaries

The builder requires the exact approval phrase:

`APPROVE OPTIONS DAY AGGS SAMPLE HANDOFF BUILD`

Safety boundaries:

- no vendor calls
- no downloads
- no DB reads or writes
- no live ingestion
- no scheduler activation
- no production export
- no `.env` changes
- no AI/trading/risk/regime/portfolio logic
- no quarantine file commits

## Files Created / Updated

- `app/vendor_flat_files/options/options_day_aggs_handoff_builder.py`
- `scripts/build_options_day_aggs_handoff_sample.py`
- `tests/unit/test_options_day_aggs_handoff_builder.py`
- `tests/scripts/test_build_options_day_aggs_handoff_sample.py`
- `docs/options_day_aggs_handoff_sample.md`

## Tests to Run

- `python -m pytest tests/unit/test_options_day_aggs_handoff_builder.py`
- `python -m pytest tests/scripts/test_build_options_day_aggs_handoff_sample.py`
- `python -m pytest tests/unit/test_options_day_aggs_parser.py tests/unit/test_options_day_aggs_normalizer.py`

## What This Step Does Not Do

- It does not export production handoff artifacts.
- It does not write a full dataset.
- It does not activate ingestion or scheduling.
- It does not alter the stock/ETF pipeline.
- It does not infer trading decisions or portfolio logic.

## Next Allowed Step

The next step is a small sample review of the JSONL artifact and then, only if needed, a narrower downstream fixture or consumer integration.
