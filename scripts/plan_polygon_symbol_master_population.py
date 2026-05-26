from __future__ import annotations


def main() -> int:
    steps = [
        "1. Preflight the manual symbol-master workflow: scripts/preflight_symbol_master_operations.py",
        "2. Run the small fixture dry-run: scripts/dry_run_polygon_symbol_master.py",
        "3. Run the live-check dry-run with a small limit: scripts/dry_run_polygon_symbol_master.py --live-check --limit 25 --max-records 1000",
        "4. Run a small confirmed-write batch only after the live-check is clean: scripts/dry_run_polygon_symbol_master.py --live-check --confirm-write --limit 25 --max-records 1000",
        "5. Assess coverage and metadata quality: scripts/assess_symbol_master_coverage.py",
        "6. Verify evidence after a confirmed write: scripts/verify_symbol_master_evidence_chain.py",
    ]
    print("no_vendor_calls=True")
    print("no_db_writes=True")
    print("safe_default_batch_size=25")
    print("max_records_recommendation=1000")
    print("required_env_preflight=none")
    print("required_env_dry_run=none")
    print("required_env_live_check=POLYGON_API_KEY")
    print("required_env_confirm_write=DATABASE_URL")
    print("required_env_coverage=DATABASE_URL")
    print("required_env_evidence=DATABASE_URL")
    print("coverage_thresholds=min_total=1 min_active=1 max_missing_exchange_ratio=0.05 max_missing_asset_type_ratio=0.05")
    print("recommended_step_order=" + " | ".join(steps))
    print("command_examples=")
    print("  scripts/preflight_symbol_master_operations.py")
    print("  scripts/dry_run_polygon_symbol_master.py")
    print("  scripts/dry_run_polygon_symbol_master.py --live-check --limit 25 --max-records 1000")
    print("  scripts/dry_run_polygon_symbol_master.py --live-check --confirm-write --limit 25 --max-records 1000")
    print("  scripts/assess_symbol_master_coverage.py --vendor polygon --min-total 1 --min-active 1")
    print("  scripts/verify_symbol_master_evidence_chain.py")
    print("escalation_path=if coverage_status is WARN or FAIL, stop confirmed writes, inspect gaps with assess_symbol_master_coverage.py, then review evidence and preflight before retrying")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
