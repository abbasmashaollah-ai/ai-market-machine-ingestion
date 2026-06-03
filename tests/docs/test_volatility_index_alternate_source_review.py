from __future__ import annotations

from pathlib import Path


def test_volatility_index_alternate_source_review_mentions_required_terms() -> None:
    path = Path("docs/volatility_index_alternate_source_review.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "vix",
        "vvix",
        "vxn",
        "rvx",
        "polygon",
        "403",
        "alternate source",
        "fmp",
        "fred",
        "cboe",
        "source attribution",
        "lineage",
        "no db writes",
        "no scheduler activation",
        "no ai machine changes",
        "writer remains blocked",
    ]:
        assert needle in text
