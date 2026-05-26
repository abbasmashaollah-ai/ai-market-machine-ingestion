from __future__ import annotations

from app.normalization.volatility_index import STARTER_VOLATILITY_INDEX_SYMBOLS
from app.sources.volatility_index_sources import build_volatility_index_source_candidates


def main() -> int:
    candidates = sorted(build_volatility_index_source_candidates(), key=lambda item: item.priority)
    preferred = candidates[0]
    print("no_vendor_calls=True")
    print("no_db_writes=True")
    print(f"selected_preferred_source={preferred.source_name}")
    print(f"priority_order={[candidate.source_name for candidate in candidates]}")
    print(f"supported_starter_symbols={list(STARTER_VOLATILITY_INDEX_SYMBOLS)}")
    for candidate in candidates:
        print(
            f"source={candidate.source_name} "
            f"status={candidate.status} "
            f"priority={candidate.priority} "
            f"supported_symbols={list(candidate.supported_symbols)} "
            f"historical_coverage_note={candidate.historical_coverage_note} "
            f"vendor_symbol_mapping_note={candidate.vendor_symbol_mapping_note} "
            f"rate_limit_cost_notes={candidate.rate_limit_cost_notes}"
        )
    print(
        "gaps=["
        "'No live vendor adapter is approved yet.', "
        "'No DB writes are performed.', "
        "'No scheduler activation is planned.'"
        "]"
    )
    print("next_required_step=approve_a_preferred_volatility_index_source_and_add_a_live_vendor_adapter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
