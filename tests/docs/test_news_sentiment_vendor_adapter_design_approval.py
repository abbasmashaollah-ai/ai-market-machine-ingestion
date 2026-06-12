from __future__ import annotations

from pathlib import Path


def test_news_sentiment_vendor_adapter_design_approval_doc() -> None:
    text = Path("docs/news_sentiment_vendor_adapter_design_approval.md").read_text(encoding="utf-8").lower()
    assert "vendor adapter design only" in text
    assert "no live vendor calls" in text
    assert "production not approved" in text
    assert "ai-market-machine-ingestion" in text
    assert "fixture -> normalizer -> jsonl writer -> jsonl reader" in text
    assert "rss" in text
    assert "polygon" in text
    assert "finnhub" in text
    assert "avoid paid vendor dependency until approved" in text
    assert "fetch raw source payload only when approved" in text
    assert "normalize into canonical handoff record shape" in text
    assert "validate through existing handoff module" in text
    assert "write jsonl handoff" in text
    assert "never interpret news" in text
    assert "vendor" in text
    assert "source_dataset" in text
    assert "producer_run_id" in text
    assert "generated_at" in text
    assert "schema_version" in text
    assert "record_count" in text
    assert "source_sha256" in text
    assert "batch_sha256" in text
    assert "no secrets" in text
    assert "no tokenized urls" in text
    assert "no unsafe source_file_path" in text
    assert "dry-run mode" in text
    assert "rejection evidence preserved" in text
    assert "idempotency" in text
    assert "raw/vendor sentiment only" in text
    assert "no ai sentiment" in text
    assert "no trading signal" in text
    assert "no regime/risk/portfolio interpretation" in text
    assert "no credentials" in text
    assert "no db writes" in text
    assert "no data repo api calls" in text
    assert "no scheduler" in text
    assert "credential rotation still required" in text
