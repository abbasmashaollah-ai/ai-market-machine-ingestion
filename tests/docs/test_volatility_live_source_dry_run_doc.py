from __future__ import annotations

from pathlib import Path


def test_volatility_live_dry_run_doc_mentions_required_terms() -> None:
    path = Path("docs/volatility_index_live_dry_run.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "volatility index live dry run",
        "manual",
        "confirm-live",
        "vix",
        "vvix",
        "vxn",
        "rvx",
        "no db writes",
        "no scheduler activation",
        "no persistence",
        "entitlement",
    ]:
        assert needle in text
