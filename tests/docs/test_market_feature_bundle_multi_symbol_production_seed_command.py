from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_production_seed_command_doc_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_production_seed_command.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "dedicated multi-symbol production seed command scaffold",
        "default dry-run/no-write mode",
        "guarded --execute branch exists for the symbol-agnostic writer contract",
        "production write requires explicit second approval",
        "production write currently blocked unless implementation is explicitly approved",
        "tests use injected fake writer only",
        "qqq/iwm/dia",
        "no scheduler activation",
        "no broad backfill",
        "no automated recurring job",
        "no ai machine runtime wiring",
        "no db writes in tests",
        "no vendor calls",
        "no live api calls",
        "idempotency_key_prefix only",
        "safe json summary",
        "data api verification still required after any future write",
        "production execution still requires user-run command and verification",
    ]:
        assert needle in text
