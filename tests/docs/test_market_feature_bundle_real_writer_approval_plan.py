from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_real_writer_approval_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_real_writer_approval_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "market_feature_bundle",
        "real-writer approval plan",
        "app/writers/market_feature_bundle_writer.py",
        "app/handoff/market_feature_bundle_handoff.py",
        "outside app/features",
        "app/features remains calculation-only",
        "ai-market-machine-data",
        "market_feature_bundle_snapshots",
        "get /internal/read/market-feature-bundle/{universe}",
        "build_market_feature_bundle_producer_payload",
        "idempotency_key",
        "observation_date",
        "universe",
        "schema_version",
        "dataset_version",
        "safe test db",
        "explicit approval",
        "no db writes",
        "no vendor calls",
        "no scheduler activation",
        "no data repo changes",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "no portfolio logic",
        "no risk posture",
    ]:
        assert needle in text

