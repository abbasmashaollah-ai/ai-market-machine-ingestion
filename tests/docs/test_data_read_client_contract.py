from pathlib import Path


def test_data_read_client_contract_covers_shared_read_boundary() -> None:
    text = Path("docs/data_read_client_contract.md").read_text(encoding="utf-8")
    required_phrases = [
        "DataReadClient",
        "ai-market-machine-data",
        "certified OHLCV",
        "get_certified_ohlcv_history",
        "X-Ops-Internal-Token",
        "AI_MARKET_MACHINE_DATA_BASE_URL",
        "OPS_INTERNAL_TOKEN",
        "read-only",
        "GET-only",
        "no vendor fallback",
        "no DB writes",
        "no AI interpretation",
        "sector_rotation",
        "breadth",
        "no scheduler activation",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"

