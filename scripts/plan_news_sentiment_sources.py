from __future__ import annotations

from app.sources.news_sentiment_sources import build_news_sentiment_source_candidates


def main() -> int:
    candidates = sorted(build_news_sentiment_source_candidates(), key=lambda item: item.priority)
    print("no_vendor_calls=True")
    print("no_db_reads=True")
    print("no_db_writes=True")
    print(f"priority_order={[candidate.source_name for candidate in candidates]}")
    print(f"supported_record_shapes={sorted({shape for candidate in candidates for shape in candidate.supported_record_shapes})}")
    for candidate in candidates:
        print(
            f"source={candidate.source_name} "
            f"status={candidate.status} "
            f"priority={candidate.priority} "
            f"supported_record_shapes={list(candidate.supported_record_shapes)} "
            f"coverage_note={candidate.coverage_note} "
            f"lineage_note={candidate.lineage_note} "
            f"quality_note={candidate.quality_note}"
        )
    print(
        "gaps=["
        "'No live vendor adapter is approved yet.', "
        "'No persistence contract is approved yet.', "
        "'No scheduler activation is planned.'"
        "]"
    )
    print("next_required_step=approve_the_news_sentiment_data_contract_and_select_the_first_live_source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
