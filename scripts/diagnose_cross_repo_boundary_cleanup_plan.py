from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify cross-repo boundary cleanup actions.")
    parser.parse_args()

    print("cleanup_plan_status=planning_only_not_enabled")
    print("destructive_actions_enabled=false")
    print("boundary_owner_data=ai-market-machine-data")
    print("boundary_owner_ingestion=ai-market-machine-ingestion")
    print("keep_in_data=schema,migrations,canonical_read_apis,grafana_read_models,stored_evidence_health")
    print("move_to_ingestion=vendor_fetching,daily_runners,backfills,flat_files,websocket,scheduler_execution")
    print("deprecate_in_data=direct_vendor_ingestion,old_runtime_ingestion_paths,direct_scheduler_execution")
    print("hygiene_cleanup=.env,.venv,.pytest_cache,__pycache__,logs_in_handoff_zips")
    print(
        "required_next_steps="
        "confirm_data_repo_audit,mark_deprecated_paths,remove_runtime_invocation_paths_after_migration,"
        "clean_handoff_packaging"
    )
    print("production_switch_enabled=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
