# News Sentiment Fixture Normalizer Implementation

- Final filename: `docs/news_sentiment_fixture_normalizer_implementation.md`
- Status: FIXTURE NORMALIZER ONLY / NO LIVE VENDOR CALLS / PRODUCTION NOT APPROVED
- Repository: `ai-market-machine-ingestion`
- Purpose: define the local fixture parser/normalizer that converts synthetic news records into canonical handoff records
- Source handoff module: `app/handoff/news_sentiment_handoff.py`
- Normalizer file: `app/handoff/news_sentiment_fixture_normalizer.py`
- Test file: `tests/unit/test_news_sentiment_fixture_normalizer.py`
- Fixture file: `tests/fixtures/news_sentiment_fixture_sample.json`

## Input fixture shape

- `id`
- `source`
- `domain`
- `title`
- `published_at`
- `collected_at`
- `url`
- `summary`
- `symbols`
- `topics`
- `sentiment_score`
- `sentiment_label`

## Output canonical handoff shape

- `news_id`
- `vendor_article_id`
- `vendor`
- `source_dataset`
- `source_name`
- `source_domain`
- `headline`
- `published_at`
- `collected_at`
- `producer_run_id`
- `url`
- `canonical_url`
- `summary`
- `content_snippet`
- `language`
- `author`
- `image_url`
- `updated_at`
- `tickers`
- `entities`
- `topics`
- `countries`
- `asset_classes`
- `relevance_score`
- `raw_sentiment_score`
- `raw_sentiment_label`
- `sentiment_source`
- `source_sha256`
- `source_file_name`
- `source_file_path`
- `lineage`
- `warnings`

## Mapping rules

- `title` -> `headline`
- `symbols` -> `tickers`
- `source` -> `source_name`
- `domain` -> `source_domain`
- `sentiment_score` -> `raw_sentiment_score`
- `sentiment_label` -> `raw_sentiment_label`
- batch metadata stamps `vendor`, `source_dataset`, and `producer_run_id`

## Timestamp normalization

- timestamps are normalized to ISO 8601 UTC strings
- `published_at` is required
- `collected_at` is required or defaulted from batch metadata when fixture-safe

## Deterministic `news_id` policy

- use provided `news_id` if present
- otherwise derive a deterministic `news_id` from batch metadata and stable record fields

## Raw sentiment preservation

- keep vendor/raw sentiment fields only
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio interpretation

## Validation / rejection

- all normalized records are validated with `app/handoff/news_sentiment_handoff.py`
- invalid fixtures are quarantined in-memory and reported
- secret-like URLs and unsafe paths are rejected

## Dry-run behavior

- the dry-run script can now accept `--input-fixture tests/fixtures/news_sentiment_fixture_sample.json`
- the dry run remains fixture-only
- no vendor calls
- no DB writes

## Future next step

- design a selected vendor adapter or extend end-to-end fixture handoff validation

## Boundary confirmations

- fixture normalizer only
- no live vendor calls
- no DB writes
- no data repo API calls
- no scheduler
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio logic
- no secrets stored
- credential rotation still required before production/online use
