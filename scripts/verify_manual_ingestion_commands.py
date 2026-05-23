from __future__ import annotations

import importlib


MODULES = (
    "scripts.inspect_fred_macro_checkpoint",
    "scripts.preview_fred_macro_incremental",
    "scripts.dry_run_fred_macro_incremental",
    "scripts.persist_fred_macro_incremental",
    "scripts.dry_run_polygon_ohlcv_incremental",
    "scripts.persist_polygon_ohlcv_incremental",
    "scripts.run_polygon_ohlcv_tiny_universe_check",
    "scripts.plan_polygon_ohlcv_backfill",
    "scripts.plan_polygon_ohlcv_daily_update",
    "scripts.plan_polygon_ohlcv_scheduler_cycle",
    "scripts.plan_polygon_ohlcv_symbol_universe",
    "scripts.preflight_polygon_ohlcv_operations",
    "scripts.verify_polygon_preflight_recommendations",
    "scripts.generate_polygon_ohlcv_operator_runbook",
    "scripts.run_polygon_ohlcv_scheduler_cycle",
    "scripts.verify_polygon_scheduler_disabled",
    "scripts.diagnose_us_market_calendar_readiness",
    "scripts.diagnose_polygon_quota_readiness",
    "scripts.diagnose_polygon_flatfile_readiness",
    "scripts.diagnose_polygon_flatfile_layout_readiness",
    "scripts.plan_polygon_flatfile_discovery",
    "scripts.run_polygon_ohlcv_daily_update",
    "scripts.run_polygon_ohlcv_chunked_backfill",
    "scripts.inspect_ingestion_run_history",
    "scripts.inspect_data_quality_results",
    "scripts.inspect_data_lineage",
    "scripts.verify_polygon_ohlcv_evidence_chain",
    "scripts.inspect_polygon_ohlcv_checkpoint",
    "scripts.verify_polygon_ohlcv_rows",
    "scripts.diagnose_ohlcv_overlap",
    "scripts.diagnose_ohlcv_coverage",
    "scripts.fill_polygon_ohlcv_gaps",
)


def main() -> int:
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        main_entry = getattr(module, "main", None)
        if not callable(main_entry):
            raise RuntimeError(f"{module_name} does not expose a callable main()")
        print(f"verified_import={module_name} main=callable")
    print("manual-ingestion-commands: import verification complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
