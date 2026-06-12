# News Sentiment RSS Sample Adapter Implementation

- Final filename: `docs/news_sentiment_rss_sample_adapter_implementation.md`
- Status: STORED-SAMPLE RSS ADAPTER ONLY / NO LIVE VENDOR CALLS / PRODUCTION NOT APPROVED
- Repository: `ai-market-machine-ingestion`
- Purpose: normalize stored RSS-style sample records into canonical News + Sentiment handoff records
- Source design approval doc: `docs/news_sentiment_vendor_adapter_design_approval.md`
- Adapter file: `app/handoff/news_sentiment_rss_sample_adapter.py`
- Test file: `tests/unit/test_news_sentiment_rss_sample_adapter.py`
- Fixture file: `tests/fixtures/news_sentiment_rss_sample.json`
- Dry-run script update: `scripts/run_news_sentiment_handoff_dry_run.py`

## Stored sample input shape

- `guid`
- `title`
- `link`
- `source_name`
- `source_domain`
- `published`
- `collected_at`
- `summary`
- `categories`
- `symbols`
- `sentiment_score`
- `sentiment_label`

## Canonical output shape

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

- `guid` -> `vendor_article_id`
- `title` -> `headline`
- `link` -> `url` and `canonical_url`
- `source_name` / `source_domain` -> `source_name` / `source_domain`
- `published` -> `published_at`
- `categories` -> `topics`
- `symbols` -> `tickers`
- `sentiment_score` -> `raw_sentiment_score`
- `sentiment_label` -> `raw_sentiment_label`

## Timestamp normalization

- timestamps are normalized to ISO 8601 UTC strings
- `published_at` is required
- `collected_at` is required or defaulted from batch metadata when fixture-safe

## Deterministic `news_id` policy

- use provided `news_id` if present
- otherwise derive a deterministic `news_id` from batch metadata and stable record fields

## Validation / rejection behavior

- normalized records are validated with `app/handoff/news_sentiment_handoff.py`
- invalid sample items are quarantined in-memory and reported
- malformed or secret-like URLs are rejected

## Security / no-secret behavior

- no secrets in fixtures
- no tokenized URLs
- no unsafe `source_file_path`
- no production endpoints
- no live network calls

## Raw sentiment boundary

- raw/vendor-provided sentiment only
- no AI sentiment
- no trading signal
- no regime/risk/portfolio interpretation

## Future next step

- data-repo handoff acceptance/import path or live adapter approval

## Boundary confirmations

- stored-sample adapter only
- no live vendor calls
- no credentials
- no DB writes
- no data repo API calls
- no scheduler
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio logic
- no secrets stored
- credential rotation still required before production/online use
