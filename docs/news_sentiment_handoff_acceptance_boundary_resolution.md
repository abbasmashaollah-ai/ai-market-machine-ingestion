# News/Sentiment Handoff Acceptance Boundary Resolution

## Boundary Decision
The News/Sentiment handoff acceptance runtime helper has been refactored into ingestion-owned JSONL parsing, validation, and quarantine behavior. It no longer imports data-repo ORM modules.

## Runtime File Ownership
`app/warehouse/news_sentiment_handoff_acceptance.py` is now committed ingestion-owned source.

## Test Ownership
`tests/warehouse/test_news_sentiment_handoff_acceptance.py` validates ingestion-owned handoff behavior only and does not import `app.database.*`.

## Why This Is Compliant
The runtime helper now stays within the ingestion boundary and does not depend on warehouse ORM modules.

## Generated Outputs
The `outputs/` trees are generated local artifacts. They are now ignored and should not be committed.

## Recommended Next Step
Commit the ingestion-owned helper and test, then proceed with News/Sentiment contract cleanup.

## Readiness
The ingestion-owned helper and test are ready to be committed.
