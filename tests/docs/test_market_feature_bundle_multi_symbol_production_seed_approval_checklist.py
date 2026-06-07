from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_production_seed_approval_checklist_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_production_seed_approval_checklist.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "production seed/write approval checklist",
        "qqq/iwm/dia",
        "fixture evidence is not production evidence",
        "explicit user approval required",
        "observation_date `2026-01-15`",
        "dataset_version `production_pilot.v1`",
        "schema_version `market_feature_bundle.v1`",
        "validation_status `pass`",
        "coverage_status `complete`",
        "quality_status `pass`",
        "certification_status `certified` only after production validation",
        "production-safe",
        "deterministic",
        "no secrets/tokens/raw provider credentials",
        "rollback or no-op strategy",
        "data api verification command after write",
        "ai machine remains non-wired",
        "manual one-row-style write only",
        "no scheduler activation",
        "no broad backfill",
        "no automated recurring job",
        "no provider calls unless explicitly approved",
        "write only certified rows",
        "insufficient_evidence",
        "direct data api check for spy/qqq/iwm/dia",
        "qqq/iwm/dia must show certification_status certified",
        "missing evidence remains insufficient_evidence, not failure or bearish signal",
        "ai machine multi-symbol diagnostic can proceed only after verification passes",
        "no ingestion execution",
        "no db writes",
        "no vendor calls",
        "no live api calls",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text

