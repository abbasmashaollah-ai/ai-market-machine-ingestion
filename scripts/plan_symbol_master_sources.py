from __future__ import annotations

from app.sources.symbol_master_sources import build_symbol_master_source_plan


def main() -> int:
    plans = sorted(build_symbol_master_source_plan(), key=lambda item: item.priority)
    preferred = plans[0]
    print("no_vendor_calls=True dry_run=True")
    print(f"selected_preferred_source={preferred.source_name}")
    print(f"priority_order={[plan.source_name for plan in plans]}")
    for plan in plans:
        print(
            f"source={plan.source_name} "
            f"status={plan.status} "
            f"priority={plan.priority} "
            f"supported_asset_types={list(plan.supported_asset_types)} "
            f"active_delisted_support={plan.active_delisted_support} "
            f"vendor_symbol_support={plan.vendor_symbol_support} "
            f"exchange_support={plan.exchange_support} "
            f"rate_limit_cost_notes={plan.rate_limit_cost_notes}"
        )
    gaps = [
        "No vendor feed is selected for production use yet.",
        "No DB writes are performed.",
        "No scheduler activation is planned.",
    ]
    print(f"gaps={gaps}")
    print("next_required_step=approve_a_preferred_symbol_master_source_and_add_a_vendor_adapter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
