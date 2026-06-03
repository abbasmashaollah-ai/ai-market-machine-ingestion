from __future__ import annotations

from pathlib import Path


def test_volatility_index_source_entitlement_strategy_mentions_required_terms() -> None:
    path = Path("docs/volatility_index_source_entitlement_strategy.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "vix",
        "vvix",
        "vxn",
        "rvx",
        "403",
        "polygon",
        "entitlement",
        "no db writes",
        "no scheduler activation",
        "no ai machine changes",
        "writer remains blocked",
        "alternate vendor",
        "fred",
        "cboe",
        "source attribution",
        "lineage",
    ]:
        assert needle in text
