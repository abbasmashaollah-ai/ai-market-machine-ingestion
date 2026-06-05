from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_one_row_production_pilot_completion_checkpoint_mentions_required_terms() -> None:
    path = Path("docs/market_feature_bundle_one_row_production_pilot_completion_checkpoint.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "one-row production pilot completed",
        "spy",
        "production_pilot.v1",
        "write_accepted",
        "write_continued",
        "preserve_first_production_row",
        "row preserved",
        "get /internal/read/market-feature-bundle/spy",
        "structured verification passed",
        "validation_status pass",
        "certification_status certified",
        "compact_summary",
        "full_bundle_payload",
        "lineage_refs",
        "quality_result_refs",
        "observability event emitted",
        "observability summary emitted",
        "write_attempt_count 1",
        "write_success_count 1",
        "write_failure_count 0",
        "idempotency_key_prefix",
        "no scheduler activation",
        "no backfill",
        "no vendor calls",
        "no ai machine changes",
        "no data repo source changes",
        "no broad deletes",
        "no truncate",
        "no drop table",
        "no full db url",
        "no password",
        "no token",
        "no full idempotency_key",
        "credential was exposed",
        "rotate",
        "ai machine consumption remains last",
    ]:
        assert needle in text
