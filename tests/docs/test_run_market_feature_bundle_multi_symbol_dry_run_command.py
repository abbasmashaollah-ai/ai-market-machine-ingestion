from __future__ import annotations

from pathlib import Path


def test_run_market_feature_bundle_multi_symbol_dry_run_command_doc_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_dry_run_command.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "dry-run-only multi-symbol command",
        "qqq/iwm/dia",
        "existing spy-only dry-run blocker",
        "fixture payloads only",
        "no db writes",
        "no production seed/write",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no ai machine runtime wiring",
        "idempotency_key_prefix only",
        "output-file local only",
        "second explicit approval required before db write",
    ]:
        assert needle in text

