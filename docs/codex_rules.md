# Codex Rules

These rules apply to every future change in `ai-market-machine-ingestion`.

## Required Rules

- Preserve the ingestion-only boundary.
- Never add AI, signal, regime, strategy, portfolio, risk, or prediction logic.
- Never add FastAPI routes or public APIs.
- Never add Alembic migrations for canonical tables.
- Never create or alter canonical tables.
- Never call `Base.metadata.create_all()`.
- Route all database writes through `app/writers/`.
- Prefer small modular files.
- Add or update a matching `.md` documentation file for every new or materially changed code file.
- Add tests for new behavior.
- Keep Railway deployment readiness in mind.
- Do not introduce Redis, Kafka, or Celery unless explicitly requested.
- Do not import `ai-market-machine-data` internals directly unless explicitly approved.
- Treat `ai-market-machine-data` as the schema owner.
- Treat this repository as worker-only infrastructure.

## Operating Standard

If a change would weaken the ingestion boundary, it does not belong here. The default answer is to keep this repository focused on vendor fetch, normalization, validation, reconciliation, approved writes, lineage, checkpoints, and operational tracking.

## Final Checklist

Before finishing any step, Codex must verify:

1. The change stays within ingestion-only scope.
2. No AI, trading, signal, regime, strategy, portfolio, risk, or prediction logic was added.
3. No FastAPI routes or public APIs were added.
4. No canonical tables were created or altered.
5. No Alembic migration was added for canonical tables.
6. `Base.metadata.create_all()` was not introduced.
7. All database writes go through `app/writers/`.
8. A matching `.md` doc was created or updated for any new or materially changed code file.
9. Tests were added or updated for new behavior.
10. The change remains compatible with Railway deployment readiness.
11. No Redis, Kafka, or Celery dependency was introduced without explicit approval.
12. `ai-market-machine-data` remains the schema owner.
