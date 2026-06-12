# News Sentiment E2E Fixture Handoff Validation

- Final filename: `docs/news_sentiment_e2e_fixture_handoff_validation.md`
- Status: E2E FIXTURE HANDOFF VALIDATION ONLY / NO LIVE VENDOR CALLS / PRODUCTION NOT APPROVED
- Repository: `ai-market-machine-ingestion`
- Purpose: prove fixture records normalize into valid JSONL handoff records accepted by the local handoff validator
- Source handoff module: `app/handoff/news_sentiment_handoff.py`
- Source fixture normalizer: `app/handoff/news_sentiment_fixture_normalizer.py`
- Fixture file: `tests/fixtures/news_sentiment_fixture_sample.json`
- Test file: `tests/unit/test_news_sentiment_e2e_fixture_handoff.py`

## Validation flow

- fixture -> normalizer -> JSONL writer -> JSONL reader

## Fields verified

- `news_id`
- `vendor`
- `source_dataset`
- `source_name`
- `source_domain`
- `headline`
- `published_at`
- `collected_at`
- `producer_run_id`
- `raw_sentiment_score`
- `raw_sentiment_label`
- no strategy fields

## Negative validation behavior

- malformed JSONL lines are reported with line numbers
- invalid fixture records are rejected in memory
- bad records are not silently written

## Sentiment boundary

- raw/vendor-provided sentiment only
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio interpretation

## Security / no-secret behavior

- no secrets in fixtures
- no production endpoint in test fixtures
- no raw tokenized vendor URLs
- no unsafe `source_file_path`

## Future next step

- selected vendor adapter design/approval or data-repo handoff acceptance reader

## Boundary confirmations

- fixture handoff validation only
- no live vendor calls
- no DB writes
- no data repo API calls
- no scheduler
- no AI-generated sentiment
- no trading signal
- no regime/risk/portfolio logic
- no secrets stored
- credential rotation still required before production/online use
