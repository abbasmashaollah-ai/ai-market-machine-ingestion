from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_handoff_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_handoff_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "market_feature_bundle_snapshots",
        "get /internal/read/market-feature-bundle/{universe}",
        "f9c4a9b",
        "stage a",
        "stage b",
        "stage c",
        "feature-engine boundary guardrail",
        "app/features/* is calculation-only",
        "app/features/market_features/market_feature_bundle_producer_payload.py",
        "app/features/market_features/market_feature_bundle_mock_writer.py",
        "docs/feature_engine_boundary_policy.md",
        "mock-only",
        "outside app/features",
        "app/writers/",
        "app/handoff/",
        "no real writer",
        "no db writes",
        "no vendor calls",
        "no scheduler activation",
        "no data repo changes",
        "no ai machine changes",
        "no judge posture",
        "no trading decision",
        "ai machine consumption remains last",
    ]:
        assert needle in text

