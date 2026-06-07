from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_multi_symbol_execute_path_implementation_audit_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_multi_symbol_execute_path_implementation_audit.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "execute path implementation audit",
        "connect --execute to the existing production writer safely",
        "multi-symbol production seed command exists",
        "dry-run passes for qqq/iwm/dia",
        "--execute is scaffold-blocked",
        "production writer untouched",
        "writer function entrypoints",
        "expected payload shape",
        "required fields",
        "idempotency behavior",
        "duplicate/no-op behavior",
        "conflict behavior",
        "rollback/error behavior",
        "db adapter contract",
        "required env vars without values",
        "symbol-agnostic or spy-specific",
        "qqq/iwm/dia payloads",
        "exact adapter call needed",
        "exact env gate needed",
        "exact approval gate needed",
        "payload conversion",
        "certification_status conversion from production_candidate to certified",
        "per-symbol write result collection",
        "no-op/idempotent result handling",
        "post-write direct data api verification command",
        "safe json output without secrets/full idempotency keys",
        "payload-shape risk",
        "writer compatibility risk",
        "idempotency/duplicate risk",
        "rollback/no-op risk",
        "partial-write risk",
        "env-var/secrets risk",
        "wrong-symbol risk",
        "stale-date risk",
        "data api verification risk",
        "go_now",
        "no_go",
        "go_after_implementation",
        "recommended next single step",
        "no db writes",
        "no production seed/write",
        "no vendor calls",
        "no live api calls",
        "no scheduler activation",
        "no production changes",
        "no ai machine runtime wiring",
        "no secrets committed",
    ]:
        assert needle in text

