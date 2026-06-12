# News Sentiment JSONL Handoff Implementation

- Final filename: `docs/news_sentiment_jsonl_handoff_implementation.md`
- Status: LOCAL JSONL HANDOFF ONLY / NO LIVE VENDOR CALLS / PRODUCTION NOT APPROVED
- Repository: `ai-market-machine-ingestion`
- Purpose: define the local JSONL handoff writer/reader that prepares News + Sentiment records for the data repo contract
- Source data repo contract: `docs/news_sentiment_ingestion_handoff_contract.md`
- Writer file: `app/handoff/news_sentiment_handoff.py`
- Reader file: `app/handoff/news_sentiment_handoff.py`
- Test file: `tests/unit/test_news_sentiment_handoff.py`
- Dry-run script file: `scripts/run_news_sentiment_handoff_dry_run.py`

## JSONL shape

- one JSON object per line
- UTF-8 encoded
- deterministic field names
- replayable
- idempotent
- no secrets
- no raw tokenized vendor URLs
- no unsafe `source_file_path`
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio interpretation

## Required batch metadata

- `producer_run_id`
- `source_dataset`
- `vendor`
- `generated_at`
- `schema_version`
- `record_count`
- `source_sha256` or `batch_sha256` if applicable

## Required record fields

- `news_id` or deterministic ID
- `vendor_article_id` when available
- `vendor`
- `source_dataset`
- `source_name`
- `source_domain`
- `headline`
- `published_at`
- `collected_at`
- `producer_run_id`

## Optional record fields

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
- `source_file_path` only if safe and non-secret
- `lineage`
- `warnings`

## Validation rules

- validate required fields
- validate ISO 8601 timestamps
- validate JSON-compatible context fields
- validate `raw_sentiment_score` between `-1` and `1` when present
- validate no secret-like content in URL/path/metadata
- validate `source_file_path` safety
- reject any strategy-like fields

## Quarantine / rejection

- invalid records are rejected and captured in summary
- malformed JSONL lines are reported with line numbers
- optional quarantine output preserves rejected record evidence in a local safe path only
- bad records must not be silently dropped

## Idempotency policy

- preferred: `vendor + source_dataset + vendor_article_id`
- fallback: `vendor + source_dataset + canonical_url/url + published_at`

## Security rules

- no credentials or secrets in JSONL
- no production endpoint in file
- no unsafe `source_file_path`
- no raw tokenized vendor URLs

## Local-first policy

- fixture parser first
- normalizer
- validator / quarantine
- JSONL writer
- JSONL reader
- dry-run report
- no live vendor calls until approved

## Future next step

- implement a fixture parser/normalizer for a selected news source in `ai-market-machine-ingestion`

## Boundary confirmations

- local handoff only
- no live vendor calls
- no DB writes
- no data repo API calls
- no scheduler
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio logic
- no secrets stored
- credential rotation still required before production/online use
