# Manual Ingestion Command Verification

`scripts/verify_manual_ingestion_commands.py` is a manual, Railway-safe verification script.

## Scope

The script imports these manual command modules:

- `scripts.inspect_fred_macro_checkpoint`
- `scripts.preview_fred_macro_incremental`
- `scripts.dry_run_fred_macro_incremental`
- `scripts.persist_fred_macro_incremental`
- `scripts.dry_run_polygon_ohlcv_incremental`
- `scripts.persist_polygon_ohlcv_incremental`
- `scripts.run_polygon_ohlcv_tiny_universe_check`
- `scripts.plan_polygon_ohlcv_backfill`
- `scripts.plan_polygon_ohlcv_daily_update`
- `scripts.plan_polygon_ohlcv_scheduler_cycle`
- `scripts.plan_polygon_ohlcv_symbol_universe`
- `scripts.preflight_polygon_ohlcv_operations`
- `scripts.verify_polygon_preflight_recommendations`
- `scripts.generate_polygon_ohlcv_operator_runbook`
- `scripts.run_polygon_ohlcv_scheduler_cycle`
- `scripts.verify_polygon_scheduler_disabled`
- `scripts.diagnose_ingestion_monitoring_readiness`
- `scripts.diagnose_ingestion_retry_recovery_readiness`
- `scripts.diagnose_ingestion_failure_recovery_runbook`
- `scripts.diagnose_polygon_production_enablement_readiness`
- `scripts.diagnose_market_calendar_production_upgrade`
- `scripts.diagnose_market_calendar_provider_strategy`
- `scripts.diagnose_market_calendar_provider_interface`
- `scripts.diagnose_market_calendar_fallback_behavior`
- `scripts.diagnose_market_calendar_schema_handoff`
- `scripts.diagnose_us_market_calendar_readiness`
- `scripts.diagnose_polygon_quota_readiness`
- `scripts.diagnose_polygon_flatfile_readiness`
- `scripts.diagnose_polygon_flatfile_layout_readiness`
- `scripts.diagnose_polygon_flatfile_official_layout_capture`
- `scripts.diagnose_polygon_flatfile_config_readiness`
- `scripts.diagnose_polygon_flatfile_storage_policy`
- `scripts.diagnose_polygon_flatfile_manifest_readiness`
- `scripts.diagnose_polygon_flatfile_integrity_readiness`
- `scripts.diagnose_polygon_flatfile_quarantine_readiness`
- `scripts.diagnose_polygon_flatfile_parse_readiness`
- `scripts.diagnose_polygon_flatfile_download_readiness`
- `scripts.diagnose_polygon_flatfile_persistence_readiness`
- `scripts.diagnose_polygon_flatfile_e2e_readiness`
- `scripts.plan_polygon_flatfile_discovery`
- `scripts.run_polygon_ohlcv_daily_update`
- `scripts.run_polygon_ohlcv_chunked_backfill`
- `scripts.inspect_polygon_ohlcv_checkpoint`
- `scripts.verify_polygon_ohlcv_rows`
- `scripts.inspect_data_lineage`
- `scripts.verify_polygon_ohlcv_evidence_chain`
- `scripts.diagnose_ohlcv_overlap`
- `scripts.diagnose_ohlcv_coverage`
- `scripts.fill_polygon_ohlcv_gaps`

It verifies each module exposes a callable `main()` entrypoint and prints a safe inventory line for each.

## Safety

The script does not:

- require `FRED_API_KEY`
- require `DATABASE_URL`
- call vendors
- write to the database
- write lineage data
- schedule work
- run ingestion
- persist checkpoints
- run automatically on Railway startup

This is an operator-run verification only.

`ai-market-machine-data` remains the schema owner.
