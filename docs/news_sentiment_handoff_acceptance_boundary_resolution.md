# News/Sentiment Handoff Acceptance Boundary Resolution

## Boundary Decision
The News/Sentiment handoff acceptance runtime helper is ingestion-owned JSONL parsing, validation, and quarantine behavior. It no longer imports data-repo ORM modules.

## Runtime File Ownership
`app/warehouse/news_sentiment_handoff_acceptance.py` is ingestion-owned source.

## Test Ownership
`tests/warehouse/test_news_sentiment_handoff_acceptance.py` validates ingestion-owned handoff behavior only and does not import `app.database.*`.

## Why This Is Compliant
The runtime helper now stays within the ingestion boundary and does not depend on warehouse ORM modules.

## Generated Outputs
The `outputs/` trees are generated local artifacts. They are now ignored and should not be committed.

## Recommended Next Step
Keep the ingestion-owned helper and test aligned with the News/Sentiment contract and data-side read boundary.

## Readiness
The ingestion-owned helper is documented as settled ingestion-side boundary behavior alongside its tests.
