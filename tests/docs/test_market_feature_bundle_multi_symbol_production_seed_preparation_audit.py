from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_production_seed_preparation_audit_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_production_seed_preparation_audit.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "controlled manual production seed/write",
        "qqq/iwm/dia",
        "approved preparation only",
        "no execution yet",
        "no scheduler activation",
        "no broad backfill",
        "no automated recurring job",
        "no ai machine runtime wiring",
        "spy certified",
        "qqq/iwm/dia missing / warn / uncertified",
        "fixture dry-run payloads exist and validate",
        "fixture evidence is not production evidence",
        "market_feature_bundle",
        "production_pilot",
        "manual runner",
        "writer/persist path",
        "certification/validation gate",
        "idempotency behavior",
        "post-write verification",
        "safest likely existing command or state if none exists",
        "required env vars without printing values",
        "observation_date `2026-01-15`",
        "dataset_version `production_pilot.v1`",
        "explicit second approval required before db write",
        "dry-run/no-write command must pass first",
        "validation_status `pass`",
        "coverage_status `complete`",
        "quality_status `pass`",
        "certification_status `certified`",
        "deterministic idempotency required",
        "rollback or no-op strategy required",
        "post-write direct data api verification required",
        "no ingestion execution",
        "no db writes",
        "no vendor calls",
        "no live api calls",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
        "if a safe dry-run/no-write path exists, run dry-run next after user approval",
        "if no safe path exists, create a dry-run-only manual seed command first",
    ]:
        assert needle in text

