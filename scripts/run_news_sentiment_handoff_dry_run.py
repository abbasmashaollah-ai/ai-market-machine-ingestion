from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.handoff.news_sentiment_fixture_normalizer import (
    NewsSentimentBatchMetadata,
    load_fixture_news_records,
    normalize_fixture_news_records,
)
from app.handoff.news_sentiment_rss_sample_adapter import load_rss_sample_items, normalize_rss_sample_items
from app.handoff.news_sentiment_handoff import DEFAULT_FIXTURE_BATCH_METADATA, write_news_sentiment_handoff_jsonl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the news/sentiment JSONL handoff locally.")
    parser.add_argument("--output-file", help="Optional local JSONL output file.")
    parser.add_argument("--summary-only", action="store_true", help="Print a compact JSON summary only.")
    parser.add_argument(
        "--input-fixture",
        default="tests/fixtures/news_sentiment_fixture_sample.json",
        help="Local fixture JSON file to normalize.",
    )
    parser.add_argument(
        "--rss-sample-file",
        help="Optional stored-sample RSS JSON file to normalize instead of the standard fixture file.",
    )
    args = parser.parse_args(argv)

    batch_metadata = DEFAULT_FIXTURE_BATCH_METADATA
    if args.rss_sample_file:
        raw_records = load_rss_sample_items(args.rss_sample_file)
        normalized = normalize_rss_sample_items(raw_records, batch_metadata=batch_metadata)
        input_label = str(args.rss_sample_file)
    else:
        raw_records = load_fixture_news_records(args.input_fixture)
        normalized = normalize_fixture_news_records(raw_records, batch_metadata=batch_metadata)
        input_label = str(args.input_fixture)
    output_path = Path(args.output_file) if args.output_file else Path("outputs") / "handoff" / "news_sentiment" / "news_sentiment_fixture.jsonl"
    write_result = write_news_sentiment_handoff_jsonl(normalized.normalized_records, output_path, batch_metadata=batch_metadata)
    payload = {
        "input_fixture": input_label,
        "records_received": len(raw_records),
        "records_normalized": len(normalized.normalized_records),
        "records_rejected": len(normalized.rejected_records),
        "records_written": write_result.records_written,
        "no_vendor_calls": True,
        "no_db_writes": True,
        "no_ai_sentiment": True,
        "no_trading_signals": True,
        "no_regime_risk_portfolio_logic": True,
    }
    if not args.summary_only:
        payload["normalized_records"] = list(normalized.normalized_records)
        payload["rejected_records"] = list(normalized.rejected_records)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
