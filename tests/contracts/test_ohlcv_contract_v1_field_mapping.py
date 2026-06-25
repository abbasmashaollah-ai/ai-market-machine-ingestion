from pathlib import Path


def test_ohlcv_contract_v1_field_mapping_source_mentions_v1_aliases() -> None:
    source = Path(__file__).resolve().parents[2] / "app" / "vendor_flat_files" / "ohlcv_handoff_builder.py"
    text = source.read_text(encoding="utf-8")

    for required_text in [
        "observation_date",
        "trade_date",
        "vendor",
        "source_vendor",
        "adjusted_status",
        "adjustment_status",
    ]:
        assert required_text in text


def test_ohlcv_contract_v1_field_mapping_doc_mentions_inventory_differences() -> None:
    doc = (
        Path(__file__).resolve().parents[3]
        / "ai-market-machine-data"
        / "docs"
        / "ohlcv_handoff_contract_v1.md"
    )
    text = doc.read_text(encoding="utf-8")

    for required_text in [
        "observation_date",
        "market_date",
        "vendor",
        "source",
        "adjusted_status",
        "trade_date",
        "source_vendor",
    ]:
        assert required_text in text
