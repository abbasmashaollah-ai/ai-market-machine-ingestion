from pathlib import Path


def test_sector_rotation_certified_ohlcv_adapter_review_covers_blocker_and_contract() -> None:
    text = Path("docs/sector_rotation_certified_ohlcv_adapter_review.md").read_text(encoding="utf-8")
    required_phrases = [
        "DataReadClient",
        "private-read",
        "certified OHLCV",
        "build_price_history_by_symbol",
        "SPY",
        "XLK",
        "XLU",
        "X-Ops-Internal-Token",
        "auth/token",
        "no vendor calls",
        "no DB writes",
        "read-only",
        "no real writer",
        "no scheduler activation",
        "ai-market-machine-data",
        "AI Machine",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"

