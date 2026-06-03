from pathlib import Path


def test_sector_rotation_live_coverage_blocker_docs_cover_live_gap_and_boundaries() -> None:
    text = Path("docs/sector_rotation_live_coverage_blocker.md").read_text(encoding="utf-8")
    required_phrases = [
        "sector_rotation",
        "/internal/read/symbol/{symbol}/ohlcv/history",
        "SPY rows=65",
        "XLC rows=0",
        "XLK rows=0",
        "XLU rows=0",
        "coverage=MISSING",
        "certification=UNCERTIFIED",
        "real writer/persistence remains blocked",
        "scheduler activation remains blocked",
        "populate certified OHLCV",
        "symbol_master",
        "no DB writes",
        "no vendor calls",
        "no AI Machine changes",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
