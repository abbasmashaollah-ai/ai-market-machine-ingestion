# FRED Macro Preflight

This preflight stays read-only and only checks readiness for the dry-run foundation.

Checks:
- dry-run command exists
- live dry-run doc exists
- normalization module exists
- FRED_API_KEY is required only when `--live-check` is requested
- DATABASE_URL is not required yet
- starter series are configured
- forbidden imports are absent

No DB writes happen in preflight.
