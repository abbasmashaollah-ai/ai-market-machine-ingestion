from __future__ import annotations

from pathlib import Path


def test_vendor_flat_file_ohlcv_handoff_builder_implementation_mentions_required_terms() -> None:
    path = Path("docs/vendor_flat_file_ohlcv_handoff_builder_implementation.md")
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    for needle in [
        "pure local normalizer/handoff builder",
        "parsed local parser output only",
        "canonical_schema_version `canonical_ohlcv.v1`",
        "evidence_type `vendor_flat_file_ohlcv`",
        "fixture_only remains blocked from production warehouse handoff",
        "idempotency key is deterministic",
        "prefix-only safe summary",
        "no warehouse writer",
        "no downloader",
        "no vendor calls",
        "no downloads",
        "no db writes",
        "no scheduler activation",
        "no ai machine runtime wiring",
        "parser fixture output is not production evidence",
        "warehouse writer comes later after separate approval",
        "local function style",
        "no env vars read",
        "no requests/http/vendor sdk imports",
        "no db or writer imports",
        "no output files written",
    ]:
        assert needle in text
