from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_ai_machine_read_consumption_contract_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_ai_machine_read_consumption_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "ai machine read-consumption contract",
        "read-only consumption",
        "evidence, not judgment",
        "get /internal/read/market-feature-bundle/{universe}",
        "spy",
        "certified_only",
        "ai-market-machine-data",
        "market_feature_bundle",
        "market_feature_bundle_coverage",
        "compact_summary",
        "full_bundle_payload",
        "validation_status",
        "certification_status",
        "lineage_refs",
        "quality_result_refs",
        "coverage_status",
        "quality_status",
        "freshness_status",
        "missing_data_evidence",
        "stale_data_evidence",
        "certification_status must be certified",
        "validation_status must be pass",
        "coverage_status should be complete",
        "quality_status should be pass",
        "missing-data response as no evidence",
        "ai machine may interpret evidence",
        "ai machine owns judgment",
        "no judge posture",
        "no trading decision",
        "no risk posture",
        "no portfolio allocation",
        "read-only shadow consumption",
        "no capital impact",
        "no execution impact",
        "no portfolio changes",
        "no user-facing trading recommendation",
        "no ai machine code",
        "no scheduler activation",
        "no backfill",
        "no vendor live fetch",
        "no production write",
        "idempotency_key_prefix only",
        "do not log token",
        "do not log db url",
        "do not log full idempotency_key",
        "ai machine read-consumption implementation plan",
        "scheduler/backfill blocked until explicit approval",
    ]:
        assert needle in text
