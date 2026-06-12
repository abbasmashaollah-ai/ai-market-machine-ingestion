# News Sentiment Vendor Adapter Design Approval

- Final filename: `docs/news_sentiment_vendor_adapter_design_approval.md`
- Status: VENDOR ADAPTER DESIGN ONLY / NO LIVE VENDOR CALLS / PRODUCTION NOT APPROVED
- Repository: `ai-market-machine-ingestion`
- Purpose: define the first approved vendor-adapter design path for News + Sentiment without implementing live fetching

## Current implemented local path

- fixture -> normalizer -> JSONL writer -> JSONL reader

## Candidate vendor / source options

- free/local fixture source
- RSS/news feed style source
- Polygon/news style adapter if already planned
- Finnhub/news style adapter if already planned
- other future provider placeholder

## Recommendation

- start with a fixture/RSS-style adapter or stored-sample adapter first
- avoid paid vendor dependency until approved

## Proposed adapter boundary

- fetch raw source payload only when approved
- normalize into canonical handoff record shape
- validate through existing handoff module
- write JSONL handoff
- never interpret news

## Required adapter interface

- fetch or load raw records
- normalize records
- validate records
- write JSONL
- produce dry-run summary

## Required metadata

- `vendor`
- `source_dataset`
- `producer_run_id`
- `generated_at`
- `schema_version`
- `record_count`
- `source_sha256` / `batch_sha256`

## Required safety controls

- no secrets in output
- no tokenized URLs
- no unsafe `source_file_path`
- no unsafe source_file_path
- no production endpoint in fixtures/docs
- no live calls unless approved
- explicit dry-run mode

## Rejection / quarantine behavior

- malformed records must be rejected locally
- rejection evidence preserved
- bad records not silently dropped

## Idempotency

- preferred `vendor + source_dataset + vendor_article_id`
- fallback `vendor + source_dataset + canonical_url/url + published_at`

## Sentiment boundary

- preserve raw/vendor sentiment only
- no AI sentiment
- no trading signal
- no regime/risk/portfolio interpretation

## Approval gates before implementation

- selected provider/source approved
- credential policy approved if needed
- fixture/stored-sample test available
- no paid subscription dependency unless explicitly approved
- output contract verified against data repo handoff contract
- dry-run only first

## Future implementation steps

1. create provider-specific stored fixture/sample
2. build provider-specific normalizer
3. validate with local handoff writer/reader
4. add dry-run CLI path
5. only then consider live adapter

## Future next step

- implement selected stored-sample/RSS-style adapter normalizer after approval

## Boundary confirmations

- design only
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
