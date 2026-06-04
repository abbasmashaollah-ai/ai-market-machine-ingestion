from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_producer_contract_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_producer_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "market_feature_bundle",
        "market_feature_bundle_snapshots",
        "get /internal/read/market-feature-bundle/{universe}",
        "f9c4a9b",
        "observation_date",
        "generated_at",
        "universe",
        "schema_version",
        "dataset_version",
        "idempotency_key",
        "compact_summary",
        "full_bundle_payload",
        "validation_status",
        "certification_status",
        "source_repo",
        "source_run_id",
        "lineage_refs",
        "quality_result_refs",
        "deterministic",
        "no real writer",
        "no db writes",
        "no vendor calls",
        "no scheduler activation",
        "no data repo changes",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "stage b",
        "stage c",
        "stage d",
        "stage e",
        "stage f",
    ]:
        assert needle in text
