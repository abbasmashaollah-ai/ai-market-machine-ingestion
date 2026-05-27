# Event Calendar Preflight

This preflight stays read-only and only checks readiness for the event calendar foundation.

Checks:
- dry-run command exists
- source plan command exists
- foundation doc exists
- source plan doc exists
- normalization module exists
- starter event types are configured
- macro-event dry-run command exists
- macro-event source plan command exists
- macro-event foundation doc exists
- macro-event source plan doc exists
- macro-event normalization module exists
- CPI/FOMC/NFP are configured
- DATABASE_URL is not required yet
- vendor API keys are not required yet
- forbidden imports are absent

No DB writes happen in preflight.

The evidence plan remains deferred until the event-calendar persistence contract is approved.
