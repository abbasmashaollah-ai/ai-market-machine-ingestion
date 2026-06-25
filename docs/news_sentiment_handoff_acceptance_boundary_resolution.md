# News/Sentiment Handoff Acceptance Boundary Resolution

## Boundary Decision
The News/Sentiment handoff acceptance runtime helper is still deferred because it imports modules that are not present in this repository. The warehouse acceptance test has been rewritten to use ingestion-owned handoff primitives only.

## Runtime File Ownership
`app/warehouse/news_sentiment_handoff_acceptance.py` remains deferred until its missing local dependencies are resolved or the helper is moved to the data repo.

## Test Ownership
`tests/warehouse/test_news_sentiment_handoff_acceptance.py` now validates ingestion-owned handoff behavior only and does not import `app.database.*`.

## Why Deferred
The runtime helper itself still cannot be committed because its direct imports are unresolved in this repository boundary.

## Generated Outputs
The `outputs/` trees are generated local artifacts. They are now ignored and should not be committed.

## Recommended Next Step
Commit the ingestion-owned test and keep the runtime helper deferred until its missing dependencies are resolved or moved.

## Readiness
The ingestion-owned test is ready; the runtime helper remains deferred.
