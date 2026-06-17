from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_polygon_stock_day_agg_local_handoff_artifacts import (
    validate_polygon_stock_day_agg_local_handoff_artifacts,
)

EXPECTED_OUTPUT_ROOT = Path("outputs/intake_packages/polygon_stock_day_aggs")
DEFAULT_PACKAGE_ID = "polygon_stock_day_aggs_2026-06-15_2026-06-15"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a local-only data-repo intake package descriptor.")
    parser.add_argument("--manifest", required=True, help="Path to the validated local batch manifest JSON.")
    parser.add_argument("--output-dir", required=True, help="Local output directory under outputs/intake_packages/polygon_stock_day_aggs/.")
    parser.add_argument("--package-id", default=DEFAULT_PACKAGE_ID, help="Optional intake package identifier.")
    return parser


def _validate_output_dir(output_dir: Path) -> tuple[bool, str]:
    try:
        resolved = output_dir.resolve()
        allowed = EXPECTED_OUTPUT_ROOT.resolve()
        if resolved == allowed or allowed in resolved.parents:
            return True, ""
        return False, f"output_dir must be within {EXPECTED_OUTPUT_ROOT.as_posix()}"
    except Exception:
        return False, "output_dir could not be resolved safely"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_polygon_stock_day_agg_data_repo_intake_package(*, manifest_path: str | Path, output_dir: str | Path, package_id: str) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    output_dir = Path(output_dir)
    package_path = output_dir / f"{package_id}_intake_package.json"
    payload: dict[str, Any] = {
        "intake_package_attempted": True,
        "intake_package_written": False,
        "intake_package_path": str(package_path),
        "validation_passed": False,
        "total_rows_expected": 0,
        "total_rows_observed": 0,
        "blockers": [
            "descriptor-only intake package builder is allowed only after local validation passes",
            "no vendor calls, downloads, DB writes, ingestion, scheduler activation, production mutation, or data repo mutation are permitted",
        ],
        "vendor_call_attempted": False,
        "download_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "data_repo_mutation_attempted": False,
    }

    output_ok, output_error = _validate_output_dir(output_dir)
    if not output_ok:
        payload["blockers"].append(output_error)
        return payload

    validation = validate_polygon_stock_day_agg_local_handoff_artifacts(manifest_path=manifest_path)
    payload["validation_passed"] = bool(validation.get("validation_passed", False))
    payload["total_rows_expected"] = int(validation.get("total_rows_expected", 0))
    payload["total_rows_observed"] = int(validation.get("total_rows_observed", 0))
    payload["date_artifact_count_checked"] = int(validation.get("date_artifact_count_checked", 0))
    if not payload["validation_passed"]:
        payload["blockers"].append("local handoff artifacts failed validation")
        payload["validation_errors"] = validation.get("validation_errors", [])
        return payload

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_paths = []
    rows_paths = []
    for item in manifest.get("per_date_outputs", []):
        if isinstance(item, dict):
            summary_paths.append(str(item.get("summary_path", "")))
            rows_paths.append(str(item.get("rows_path", "")))

    package = {
        "package_id": package_id,
        "package_type": "data_repo_intake_descriptor",
        "dataset": "ohlcv_equity_daily",
        "source_vendor": "polygon_massive_flat_files",
        "source_dataset": "polygon_stocks_day_aggs",
        "start_date": manifest.get("start_date"),
        "end_date": manifest.get("end_date"),
        "manifest_path": str(manifest_path),
        "manifest_sha256": _sha256_file(manifest_path),
        "artifact_root": str(Path(manifest_path).parent),
        "summary_files": summary_paths,
        "rows_files": rows_paths,
        "total_rows_expected": payload["total_rows_expected"],
        "total_rows_observed": payload["total_rows_observed"],
        "total_rejected_rows": int(validation.get("total_rejected_rows", 0)),
        "date_artifact_count_checked": payload["date_artifact_count_checked"],
        "validation_passed": True,
        "production_approved": False,
        "db_write_authorized": False,
        "data_repo_mutation_authorized": False,
        "ingestion_activation_authorized": False,
        "created_by_repo": "ai-market-machine-ingestion",
        "next_repo_expected": "ai-market-machine-data",
        "preview_or_local_handoff_only": True,
    }
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload.update(
        {
            "intake_package_written": True,
            "validation_errors": [],
            "intake_package_path": str(package_path),
            "summary_files": summary_paths,
            "rows_files": rows_paths,
            "date_artifact_count_checked": payload["date_artifact_count_checked"],
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = build_polygon_stock_day_agg_data_repo_intake_package(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        package_id=args.package_id,
    )
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
