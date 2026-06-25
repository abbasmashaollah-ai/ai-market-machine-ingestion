import json
import gzip
from pathlib import Path

from scripts.write_polygon_stock_day_agg_local_handoff_artifact import (
    APPROVAL_PHRASE,
    write_polygon_stock_day_agg_local_handoff_artifact,
)


def _write_static_gzip_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write("ticker,window_start,open,high,low,close,volume,transactions\n")
        handle.write("SPY,2026-06-16,100,101,99,100.5,12345,10\n")


def test_ohlcv_contract_v1_artifact_example_rows_include_required_fields() -> None:
    input_path = Path("outputs") / "quarantine" / "contract_tests" / "polygon_stocks_day_aggs_2026-06-16.csv.gz"
    output_dir = Path("outputs") / "handoff_candidates" / "polygon_stock_day_aggs" / "contract_tests"
    _write_static_gzip_csv(input_path)

    payload = write_polygon_stock_day_agg_local_handoff_artifact(
        input_path=input_path,
        requested_date="2026-06-16",
        output_dir=output_dir,
        approve_local_handoff_write=True,
        approval_phrase=APPROVAL_PHRASE,
    )

    rows = Path(payload["output_rows_path"])
    first_row = json.loads(rows.read_text(encoding="utf-8").splitlines()[0])

    for key in [
        "trade_date",
        "source_vendor",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "adjusted",
        "adjustment_status",
        "source_file_sha256",
        "lineage_id",
        "idempotency_key",
    ]:
        assert key in first_row

    assert first_row["adjusted"] is False
    assert first_row["adjustment_status"] == "unknown_or_vendor_default"


def test_ohlcv_contract_v1_artifact_doc_mentions_required_field_contract() -> None:
    doc = (
        Path(__file__).resolve().parents[3]
        / "ai-market-machine-data"
        / "docs"
        / "ohlcv_handoff_contract_v1.md"
    )
    text = doc.read_text(encoding="utf-8")

    for required_text in [
        "trade_date",
        "source_vendor",
        "adjusted",
        "adjustment_status",
        "source_file_sha256",
        "lineage_id",
        "idempotency_key",
    ]:
        assert required_text in text
