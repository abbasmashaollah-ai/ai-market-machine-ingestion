from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_pilot_expansion_approval_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_pilot_expansion_approval_plan.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "market_feature_bundle certified pilot evidence",
        "qqq",
        "iwm",
        "dia",
        "spy: `coverage_status complete`, `quality_status pass`, `certification_status certified`",
        "qqq: `coverage_status missing`, `quality_status warn`, `certification_status uncertified`",
        "iwm: `coverage_status missing`, `quality_status warn`, `certification_status uncertified`",
        "dia: `coverage_status missing`, `quality_status warn`, `certification_status uncertified`",
        "manual approval required",
        "no automatic production writes",
        "no scheduler activation",
        "no vendor calls until explicitly approved",
        "no ai machine runtime wiring",
        "fixture/dry-run only first",
        "manual one-row-style pilot expansion",
        "preserve validation/certification gates",
        "coverage_status complete",
        "quality_status pass",
        "certification_status certified",
        "validation_status pass",
        "schema_version market_feature_bundle.v1",
        "direct data api check for spy/qqq/iwm/dia",
        "insufficient_evidence",
        "not failure or bearish signal",
        "no ingestion execution",
        "no db writes",
        "no vendor calls",
        "no live api calls",
        "no production changes",
        "no secrets committed",
    ]:
        assert needle in text

