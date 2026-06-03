from pathlib import Path


def test_sector_rotation_certified_ohlcv_reader_plan_covers_contract_and_boundaries() -> None:
    text = Path("docs/sector_rotation_certified_ohlcv_reader_plan.md").read_text(encoding="utf-8")
    required_phrases = [
        "certified OHLCV",
        "price_history_by_symbol",
        "SPY",
        "XLC",
        "XLK",
        "XLU",
        "run_sector_rotation_dry_run",
        "no vendor calls",
        "no DB writes",
        "no feature calculations beyond shaping close histories",
        "no AI interpretation",
        "no real writer",
        "no scheduler activation",
        "ai-market-machine-data",
        "AI Machine",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"

