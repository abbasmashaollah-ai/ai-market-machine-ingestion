# Fundamentals/Filings Preflight

This preflight stays read-only and only checks readiness for the fundamentals/filings foundation.

Checks:
- dry-run command exists
- source plan command exists
- foundation doc exists
- source plan doc exists
- preflight doc exists
- evidence plan doc exists
- normalization module exists
- expected record families are configured
- DATABASE_URL is not required yet
- vendor API keys are not required yet
- forbidden imports are absent

No DB writes happen in preflight.

The evidence plan remains deferred until the fundamentals/filings persistence contract is approved.
