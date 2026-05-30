# News/Sentiment Foundation

This document describes the dry-run foundation for the news/sentiment ingestion slice.
It is planning and documentation only.

## Scope

- news/sentiment only
- dry-run and normalization only
- writer-readiness planning only
- no vendor calls
- no DB reads
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Normalized Record Shape

The normalized news/sentiment record includes:

- `news_id`
- `published_at`
- `source`
- `publisher`
- `title`
- `summary`
- `url`
- `tickers`
- `sentiment_label`
- `sentiment_score`
- `raw_source_id`
- `notes`

The normalized field set is aligned to the planning contract for future data-side ownership.

## Dry-Run Contract

The dry-run command uses the deterministic manual fixture by default.
It reports:

- `record_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `tickers`
- `sources`
- `no_vendor_calls=True`
- `no_db_reads=True`
- `no_db_writes=True`

Optional flags:

- `--ticker`
- `--source`
- `--show-records`
- `--show-invalid`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
The writer plan is documentation only and does not enable persistence.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.
