from pathlib import Path


def test_sector_rotation_certified_ohlcv_live_read_plan_covers_live_flow_and_boundaries() -> None:
    text = Path("docs/sector_rotation_certified_ohlcv_live_read_plan.md").read_text(encoding="utf-8")
    required_phrases = [
        "SPY",
        "XLC",
        "XLK",
        "XLU",
        "historical_ohlcv",
        "build_price_history_by_symbol",
        "run_sector_rotation_certified_ohlcv_dry_run",
        "certified OHLCV",
        "11 observation rows",
        "1 summary row",
        "no DB writes",
        "no vendor calls",
        "no scheduler activation",
        "no real writer",
        "AI Machine",
        "human approval",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
