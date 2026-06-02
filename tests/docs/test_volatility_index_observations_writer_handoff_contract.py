from __future__ import annotations

from pathlib import Path


def test_volatility_index_observations_writer_handoff_contract_mentions_required_terms() -> None:
    path = Path("docs/volatility_index_observations_writer_handoff_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "volatility_index_observations",
        "writer handoff",
        "vix",
        "vvix",
        "vxn",
        "rvx",
        "symbol",
        "index_family",
        "observation_date",
        "source",
        "idempotency",
        "no db writes",
        "no live vendor calls",
        "no scheduler activation",
    ]:
        assert needle in text
