# Flows/Positioning Preflight

This preflight stays read-only and only checks readiness for the flows/positioning foundation.

Checks:
- dry-run command exists
- source plan command exists
- foundation doc exists
- source plan doc exists
- preflight doc exists
- evidence plan doc exists
- normalization module exists
- expected record types are configured
- expected asset classes are configured
- DATABASE_URL is not required yet
- vendor API keys are not required yet
- forbidden imports are absent

No DB writes happen in preflight.

The evidence plan remains deferred until the flows/positioning persistence contract is approved.
