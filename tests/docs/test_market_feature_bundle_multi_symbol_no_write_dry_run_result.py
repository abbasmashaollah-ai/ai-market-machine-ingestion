from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_no_write_dry_run_result_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_no_write_dry_run_result.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "no-write dry-run",
        "qqq/iwm/dia",
        "no db writes",
        "no production seed/write",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no ai machine runtime wiring",
        "no secrets printed",
        "dry-run runner",
        "accepted cli args/options",
        "whether qqq/iwm/dia supported",
        "whether spy-only",
        "fixture/local mode",
        "production writer untouched",
        "command run, if safe",
        "symbols tested or reason not run",
        "explicit statement that no db writes occurred",
        "second explicit approval before db write",
        "create/extend a dry-run-only multi-symbol command first",
    ]:
        assert needle in text

