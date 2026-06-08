from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_execute_implementation_result_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_execute_implementation_result.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "guarded --execute implementation",
        "default dry-run remains unchanged",
        "db writes require explicit approval env and db url env plus --execute",
        "tests use injected fake writer only",
        "no real db writes occurred",
        "production execution still requires user-run command and verification",
        "--execute requires the approval env gate and db url gate",
        "--execute uses per-symbol injected writer results when provided",
        "--execute collects written, idempotent_noop, conflict, and failed",
        "--execute preserves symbol-by-symbol success and failure reporting",
        "--execute exposes verification_status only when a verifier is injected",
        "--execute emits idempotency_key_prefix only, not the full key",
        "--execute emits safe json summary fields only",
        "dry-run path remains no-write",
        "dry-run path does not import the db adapter",
        "dry-run path does not call the real writer",
        "dry-run path does not call vendors",
        "dry-run path does not call live apis",
        "dry-run path does not activate the scheduler",
        "not a production seed/write",
        "not data api certification",
        "not production evidence",
        "not ai machine multi-symbol readiness yet",
        "not approval to execute a real db write",
        "request explicit second approval before any real db write",
        "verify required env vars without printing values before execution",
        "run the production write only after approval",
        "run direct data api verification after any approved write",
        "ai machine multi-symbol diagnostic remains blocked until data api shows qqq/iwm/dia certified",
        "no production seed/write",
        "no real db writes",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text
