from __future__ import annotations

import argparse
import json
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.clients.data_read_client import DataReadClient
from app.features.market_features.fixtures.sector_rotation_fixtures import build_fake_data_read_client_for_sector_rotation
from app.features.sector_rotation.sector_rotation_reader import run_sector_rotation_certified_ohlcv_dry_run
from app.features.sector_rotation.sector_rotation_report import build_sector_rotation_dry_run_report


DEFAULT_UNIVERSE = "SPY"
DEFAULT_OBSERVATION_DATE = "2026-01-15"
DEFAULT_TIMESTAMP = datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an opt-in manual shadow diagnostic for sector rotation market_feature_bundle evidence."
    )
    parser.add_argument("--enable-shadow", action="store_true", help="Enable the shadow comparison path.")
    parser.add_argument("--universe", default=DEFAULT_UNIVERSE, help="Market feature bundle universe to inspect.")
    return parser


def _base_report(*, universe: str, shadow_enabled: bool) -> dict[str, object]:
    return {
        "shadow_enabled": shadow_enabled,
        "universe": universe,
        "data_api_authoritative": False,
        "primary_output_changed": False,
        "comparison_status": "skipped",
        "no_evidence_reason": "shadow_disabled" if not shadow_enabled else "missing_configuration",
        "evidence_available": False,
        "warnings_count": 0,
        "warnings": [],
        "differences_count": 0,
        "differences": [],
        "no_capital_impact": True,
        "no_portfolio_changes": True,
        "no_user_facing_recommendation": True,
    }


def _shadow_diagnostic_to_report(diagnostic: object) -> dict[str, object]:
    if diagnostic is None:
        return {
            "evidence_available": False,
            "comparison_status": "skipped",
            "no_evidence_reason": "no_evidence",
            "warnings": [],
            "warnings_count": 0,
            "differences": [],
            "differences_count": 0,
        }

    warnings = list(getattr(diagnostic, "warnings", ()) or ())
    differences = list(getattr(diagnostic, "differences", ()) or ())
    evidence_available = bool(getattr(diagnostic, "evidence_available", False))
    if not evidence_available:
        if bool(getattr(diagnostic, "unauthorized", False)):
            no_evidence_reason = "unauthorized"
        elif bool(getattr(diagnostic, "route_failure", False)):
            no_evidence_reason = "route_failure"
        else:
            no_evidence_reason = "no_evidence"
        comparison_status = "skipped"
    else:
        no_evidence_reason = None
        comparison_status = "matched" if not differences else "differences_found"

    return {
        "evidence_available": evidence_available,
        "comparison_status": comparison_status,
        "no_evidence_reason": no_evidence_reason,
        "dataset_version": getattr(diagnostic, "dataset_version", None),
        "schema_version": getattr(diagnostic, "schema_version", None),
        "certification_status": getattr(diagnostic, "certification_status", None),
        "validation_status": getattr(diagnostic, "validation_status", None),
        "coverage_status": getattr(diagnostic, "coverage_status", None),
        "quality_status": getattr(diagnostic, "quality_status", None),
        "observation_date": getattr(diagnostic, "observation_date", None),
        "generated_at": getattr(diagnostic, "generated_at", None),
        "section_availability": getattr(diagnostic, "section_availability", {}),
        "warnings": warnings,
        "warnings_count": len(warnings),
        "differences": differences,
        "differences_count": len(differences),
    }


def _build_report(*, shadow_enabled: bool, universe: str) -> dict[str, object]:
    report = _base_report(universe=universe, shadow_enabled=shadow_enabled)
    local_client = build_fake_data_read_client_for_sector_rotation()
    local_result = run_sector_rotation_certified_ohlcv_dry_run(
        local_client,
        observation_date=DEFAULT_OBSERVATION_DATE,
        timestamp=DEFAULT_TIMESTAMP,
        enable_market_feature_bundle_shadow=False,
    )
    report["primary_output"] = build_sector_rotation_dry_run_report(local_result)

    if not shadow_enabled:
        return report

    shadow_client = DataReadClient.from_environment()
    if shadow_client is None:
        return report

    shadow_result = run_sector_rotation_certified_ohlcv_dry_run(
        local_client,
        observation_date=DEFAULT_OBSERVATION_DATE,
        timestamp=DEFAULT_TIMESTAMP,
        enable_market_feature_bundle_shadow=True,
        market_feature_bundle_client=shadow_client,
    )
    shadow_diagnostic = shadow_result.shadow_diagnostic
    report.update(_shadow_diagnostic_to_report(shadow_diagnostic))
    report["shadow_enabled"] = True
    report["universe"] = str(universe).strip().upper() or DEFAULT_UNIVERSE
    report["primary_output_changed"] = False
    report["data_api_authoritative"] = False
    report["no_capital_impact"] = True
    report["no_portfolio_changes"] = True
    report["no_user_facing_recommendation"] = True
    return report


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    with suppress(Exception):
        report = _build_report(shadow_enabled=bool(args.enable_shadow), universe=str(args.universe))
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    fallback_report = _base_report(universe=str(args.universe).strip().upper() or DEFAULT_UNIVERSE, shadow_enabled=bool(args.enable_shadow))
    sys.stdout.write(json.dumps(fallback_report, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
