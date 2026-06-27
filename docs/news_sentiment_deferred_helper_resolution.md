# News/Sentiment Helper Boundary Resolution

## Boundary Decision
The News/Sentiment helper is ingestion-owned handoff behavior only. It no longer imports `app.database.*` or data-repo ORM models.

## Runtime File Ownership
`app/warehouse/news_sentiment_handoff_acceptance.py` is an ingestion-owned JSONL parsing, validation, and quarantine helper.

## Test Ownership
`tests/warehouse/test_news_sentiment_handoff_acceptance.py` remains ingestion-owned and continues to verify handoff behavior without data ORM dependencies.

## What Changed
- Removed data-repo ORM persistence imports from the helper.
- Kept JSONL parsing and validation behavior in ingestion.
- Preserved quarantine/reporting behavior without any DB write path.

## What Remains In Data
- Warehouse persistence, read, quality, and readiness remain data-owned.
- `NewsArticle` remains the data-side persistence target.

## Why This Is Compliant
- Ingestion may parse, validate, quarantine, and produce handoff artifacts.
- Ingestion does not own warehouse persistence.
- The helper now stays within the ingestion boundary.

## Readiness
The helper is ingestion-owned source alongside its tests.
