from __future__ import annotations

import argparse

from app.normalization.news_sentiment import (
    DEFAULT_FIXTURE_RECORDS,
    normalize_news_sentiment_record,
    validate_news_sentiment_record,
)


def _build_summary(source_records: tuple[dict[str, object], ...]):
    normalized_records = tuple(normalize_news_sentiment_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_news_sentiment_record(record)}
        for record in normalized_records
        if validate_news_sentiment_record(record)
    )
    return normalized_records, invalid_records


def _emit(*, normalized_records, invalid_records, show_records: bool, show_invalid: bool) -> None:
    print(f"record_count={len(normalized_records) + len(invalid_records)}")
    print(f"normalized_count={len(normalized_records)}")
    print(f"valid_count={len(normalized_records) - len(invalid_records)}")
    print(f"invalid_count={len(invalid_records)}")
    print(f"tickers={sorted({ticker for record in normalized_records if record.tickers for ticker in record.tickers})}")
    print(f"sources={sorted({record.source for record in normalized_records if record.source})}")
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    if show_records:
        print(f"records={normalized_records}")
    if show_invalid:
        print(f"invalid_records={invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the news/sentiment foundation without database writes.")
    parser.add_argument("--ticker", action="append", help="Filter to one or more tickers.")
    parser.add_argument("--source", action="append", help="Filter to one or more sources.")
    parser.add_argument("--show-records", action="store_true", help="Show normalized records.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    args = parser.parse_args(argv)

    records = tuple(DEFAULT_FIXTURE_RECORDS)
    if args.ticker:
        allowed = set(args.ticker)
        records = tuple(
            record
            for record in records
            if isinstance(record.get("tickers"), (list, tuple)) and any(ticker in allowed for ticker in record["tickers"])
        )
    if args.source:
        allowed_sources = set(args.source)
        records = tuple(record for record in records if record.get("source") in allowed_sources)
    normalized_records, invalid_records = _build_summary(records)
    _emit(
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        show_records=args.show_records,
        show_invalid=args.show_invalid,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
