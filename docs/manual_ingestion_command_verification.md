# Manual Ingestion Command Verification

`scripts/verify_manual_ingestion_commands.py` is a manual, Railway-safe verification script.

## Scope

The script imports these manual command modules:

- `scripts.inspect_fred_macro_checkpoint`
- `scripts.preview_fred_macro_incremental`
- `scripts.dry_run_fred_macro_incremental`
- `scripts.verify_fred_macro_evidence_chain`
- `scripts.dry_run_event_calendar_foundation`
- `scripts.plan_event_calendar_sources`
- `scripts.preflight_event_calendar_operations`
- `scripts.dry_run_volatility_index_foundation`
- `scripts.dry_run_volatility_index_foundation --live-check`
- `scripts.plan_volatility_index_sources`
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
- `scripts.run_fmp_ohlcv_daily_update`
- `scripts.preflight_fmp_ohlcv_operations`
- `scripts.verify_fmp_ohlcv_evidence_chain`
- `scripts.assess_ohlcv_scheduler_readiness`
- `scripts.plan_ohlcv_scheduled_run`
- `scripts.dry_run_symbol_master_ingestion`
- `scripts.preflight_symbol_master_operations`
- `scripts.verify_symbol_master_evidence_chain`
- `scripts.plan_symbol_master_sources`
- `scripts.dry_run_polygon_symbol_master`
- `scripts.diagnose_ingestion_monitoring_readiness`
- `scripts.diagnose_ingestion_retry_recovery_readiness`
- `scripts.diagnose_ingestion_failure_recovery_runbook`
- `scripts.diagnose_polygon_production_enablement_readiness`
- `scripts.diagnose_market_calendar_production_upgrade`
- `scripts.diagnose_market_calendar_provider_strategy`
- `scripts.diagnose_market_calendar_provider_interface`
- `scripts.diagnose_market_calendar_fallback_behavior`
- `scripts.diagnose_market_calendar_schema_handoff`
- `scripts.diagnose_market_calendar_consumer_readiness`
- `scripts.diagnose_market_calendar_mock_consumer_contract`
- `scripts.diagnose_market_calendar_mock_provider`
- `scripts.diagnose_market_calendar_provider_comparison`
- `scripts.diagnose_verified_calendar_consumer_implementation_plan`
- `scripts.diagnose_canonical_contract_enforcement`
- `scripts.diagnose_cross_repo_boundary_overlap`
- `scripts.diagnose_cross_repo_boundary_cleanup_plan`
- `scripts.diagnose_ingestion_evidence_output_contract`
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

The FMP and Polygon evidence verifiers intentionally share common status helpers so their operator-facing PASS/WARN/FAIL semantics stay aligned.
The preflight commands for Polygon and FMP are documented in `docs/manual_ohlcv_preflight.md`.

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

The scheduler readiness assessor is read-only. It checks that the manual OHLCV foundation is present before any scheduler is activated, but it does not start a scheduler or change Railway startup behavior.

The scheduler plan command is also read-only. It describes the intended scheduled FMP path, while keeping Polygon backfill manual-only until explicit activation is approved later.

New ingestion domains should start from `docs/domain_vertical_slice_template.md` so the producer boundary, preflight, verifier, and evidence contracts stay consistent.

The symbol master dry-run command is the current ingestion-side foundation for future symbol master work. It remains dry-run only and does not write to the database.

The event calendar dry-run foundation is the current ingestion-side foundation for future event calendar work. It remains dry-run only and does not write to the database.

The event calendar source plan command is a read-only planning helper. It documents candidate sources before any live vendor adapter is approved.

The event calendar preflight command is a read-only readiness check. It confirms the foundation and source-plan docs exist and does not require `DATABASE_URL` or vendor keys yet.

The volatility index dry-run foundation is the current ingestion-side foundation for future volatility work. It remains dry-run only and does not call vendors or write to the database.

The volatility index source plan command is a read-only planning helper. It documents candidate sources before any live vendor adapter is approved.

The volatility index live dry-run command is still read-only, but it can use Polygon when `POLYGON_API_KEY` is present and `--live-check` is requested.

This is an operator-run verification only.

`ai-market-machine-data` remains the schema owner.
