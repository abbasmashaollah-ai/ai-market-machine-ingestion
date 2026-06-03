from pathlib import Path


def test_sector_rotation_dry_run_vertical_slice_checkpoint_covers_flow_and_boundaries() -> None:
    text = Path("docs/sector_rotation_dry_run_vertical_slice_checkpoint.md").read_text(encoding="utf-8")
    required_phrases = [
        "sector_rotation",
        "dry-run",
        "in-memory price histories",
        "relative strength",
        "leadership snapshot",
        "sector_rotation_observations",
        "sector_rotation_daily_summary",
        "mock writer",
        "no real writer",
        "no DB writes",
        "no vendor calls",
        "no scheduler activation",
        "ai-market-machine-data",
        "AI Machine",
        "scheduler activation last",
        "real writer contract review",
        "data repo write/auth path confirmation",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"

