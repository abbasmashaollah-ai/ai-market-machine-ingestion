from __future__ import annotations

from pathlib import Path


def test_volatility_index_observations_producer_contract_mentions_required_terms() -> None:
    path = Path("docs/volatility_index_observations_producer_contract.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "volatility_index_observations",
        "vix",
        "vvix",
        "vxn",
        "rvx",
        "ai-market-machine-data",
        "ai-market-machine-ingestion",
        "symbol",
        "index_family",
        "observation_date",
        "timestamp",
        "value",
        "close",
        "source",
        "source_symbol",
        "source_attribution",
        "daily_or_intraday",
        "lineage",
        "quality_status",
        "certification_status",
        "freshness_status",
        "evidence",
        "idempotency",
        "checkpoint",
        "no live vendor calls",
        "no db writes",
        "no scheduler activation",
    ]:
        assert needle in text

