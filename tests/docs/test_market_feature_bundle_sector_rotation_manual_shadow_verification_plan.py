from pathlib import Path


def test_market_feature_bundle_sector_rotation_manual_shadow_verification_plan_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_sector_rotation_manual_shadow_verification_plan.md")
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    required_phrases = [
        "manual shadow verification",
        "shadow comparison only",
        "Data API remains non-authoritative",
        "no AI Machine behavior changes",
        "shadow helper exists",
        "disabled by default",
        "baseline tests passed",
        "shadow tests passed",
        "AI_MARKET_MACHINE_DATA_BASE_URL",
        "AI_MARKET_MACHINE_DATA_INTERNAL_TOKEN",
        "no DB URL",
        "SPY",
        "GET /internal/read/market-feature-bundle/{universe}",
        "certified_only",
        "production_pilot.v1",
        "no writes",
        "no vendor calls",
        "no scheduler/backfill",
        "fetch legacy/local sector rotation input as usual",
        "explicit shadow flag enabled",
        "report differences only",
        "no changes to primary output",
        "missing config -> skip shadow",
        "401/403",
        "500",
        "timeout",
        "gated no-evidence",
        "no negative market inference",
        "no judge posture changes",
        "no trading decision changes",
        "no risk posture changes",
        "no portfolio allocation changes",
        "no capital logic changes",
        "no execution logic",
        "no production writes",
        "no DB access",
        "no vendor fetch",
        "no full idempotency_key",
        "no token/DB URL logging",
        "clear env vars after check",
        "manual shadow diagnostic script",
        "opt-in only",
        "automated tests must mock Data API",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing required phrases: {missing}"
