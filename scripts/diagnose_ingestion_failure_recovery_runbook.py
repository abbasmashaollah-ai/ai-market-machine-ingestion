from __future__ import annotations

import argparse


RUNBOOK_ENTRIES = (
    (
        "rate_limit",
        "reduce scope / wait / rerun with lower max requests",
        "scripts.diagnose_polygon_quota_readiness",
    ),
    (
        "vendor_http_error",
        "retry later / inspect vendor status manually",
        None,
    ),
    (
        "validation_failed",
        "inspect quality results / manual review",
        "scripts.inspect_data_quality_results",
    ),
    (
        "coverage_missing",
        "run coverage diagnostic / gap fill if valid trading day",
        "scripts.diagnose_ohlcv_coverage",
    ),
    (
        "checkpoint_missing",
        "inspect checkpoint / resume cautiously",
        "scripts.inspect_polygon_ohlcv_checkpoint",
    ),
    (
        "lineage_missing",
        "run evidence-chain verifier / rebuild evidence if needed",
        "scripts.verify_polygon_ohlcv_evidence_chain",
    ),
    (
        "quality_failed",
        "inspect quality results / manual review",
        "scripts.inspect_data_quality_results",
    ),
    (
        "storage_integrity_failed",
        "quarantine / manual review",
        None,
    ),
    (
        "parse_failed",
        "quarantine / manual review",
        None,
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose ingestion failure recovery runbook mappings without executing commands.")
    parser.add_argument("--vendor", default="polygon", help="Vendor name, default polygon.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    args = parser.parse_args()

    print(f"vendor={args.vendor}")
    print(f"dataset={args.dataset}")
    print("automatic_recovery_enabled=false")
    print("recovery_runbook_status=planning_only_not_enabled")
    print("safe_recommended_command_prefix=python -m")
    for failure_class, action, command in RUNBOOK_ENTRIES:
        print(f"failure_class={failure_class}")
        print(f"safe_operator_action={action}")
        if command is not None:
            print(f"recommended_command={command}")
        else:
            print("recommended_command=manual_review_only")
    print("never_execute_commands=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
