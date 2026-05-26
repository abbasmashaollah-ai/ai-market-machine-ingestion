from __future__ import annotations

from app.sources.event_calendar_sources import build_event_calendar_source_candidates


def main() -> int:
    candidates = sorted(build_event_calendar_source_candidates(), key=lambda item: item.priority)
    preferred_by_type = {}
    for candidate in candidates:
        for event_type in candidate.supported_event_types:
            preferred_by_type.setdefault(event_type, candidate.source_name)
    print("no_vendor_calls=True")
    print("no_db_writes=True")
    print(f"priority_order={[candidate.source_name for candidate in candidates]}")
    print(f"supported_event_types={sorted({event_type for candidate in candidates for event_type in candidate.supported_event_types})}")
    print(f"selected_preferred_source_by_event_type={preferred_by_type}")
    for candidate in candidates:
        print(
            f"source={candidate.source_name} "
            f"status={candidate.status} "
            f"priority={candidate.priority} "
            f"supported_event_types={list(candidate.supported_event_types)} "
            f"coverage_note={candidate.coverage_note} "
            f"timezone_handling_note={candidate.timezone_handling_note} "
            f"rate_limit_cost_notes={candidate.rate_limit_cost_notes}"
        )
    print(
        "gaps=["
        "'No live vendor adapter is approved yet.', "
        "'No persistence contract is approved yet.', "
        "'No scheduler activation is planned.'"
        "]"
    )
    print("next_required_step=approve_the_event_calendar_data_contract_and_select_the_first_live_source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
