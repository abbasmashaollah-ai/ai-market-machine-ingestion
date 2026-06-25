from app.handoff.news_sentiment_handoff import DEFAULT_FIXTURE_BATCH_METADATA, DEFAULT_FIXTURE_RECORDS


def test_news_sentiment_contract_v1_artifact_shape_covers_required_fields() -> None:
    record = DEFAULT_FIXTURE_RECORDS[0]
    required_fields = {
        "headline",
        "summary",
        "content_snippet",
        "published_at",
        "collected_at",
        "raw_sentiment_label",
        "raw_sentiment_score",
        "source_dataset",
        "source_name",
        "source_domain",
        "vendor",
        "source_file_name",
        "source_file_path",
        "lineage",
        "warnings",
        "source_sha256",
        "producer_run_id",
    }
    assert required_fields <= set(record)
    assert DEFAULT_FIXTURE_BATCH_METADATA.producer_run_id == record["producer_run_id"]
    assert DEFAULT_FIXTURE_BATCH_METADATA.source_dataset == record["source_dataset"]
    assert DEFAULT_FIXTURE_BATCH_METADATA.vendor == record["vendor"]


def test_news_sentiment_contract_v1_artifact_shape_has_no_strategy_fields() -> None:
    record = DEFAULT_FIXTURE_RECORDS[0]
    forbidden_fields = {"buy_signal", "sell_signal", "bullish", "bearish", "regime_impact", "risk_posture", "portfolio_action"}
    assert forbidden_fields.isdisjoint(record)


def test_news_sentiment_contract_v1_artifact_shape_requires_evidence_fields() -> None:
    record = dict(DEFAULT_FIXTURE_RECORDS[0])
    for field in ("source_sha256", "source_file_name", "source_file_path"):
        assert field in record
        assert record[field]
