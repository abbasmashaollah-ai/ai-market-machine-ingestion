from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

POLYGON_FLAT_FILE_CONFIG_NAMES = (
    "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
    "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
    "POLYGON_FLAT_FILE_ENDPOINT",
    "POLYGON_FLAT_FILE_BUCKET",
    "POLYGON_FLAT_FILE_PREFIX",
)
AWS_GENERIC_CONFIG_NAMES = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "AWS_S3_BUCKET",
    "AWS_S3_PREFIX",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only credential classification preflight for Polygon flat-file sector ETF readiness."
    )
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _present_names(env: dict[str, str], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if env.get(name)]


def _missing_names(env: dict[str, str], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if not env.get(name)]


def _config_classification(*, polygon_present: bool, aws_present: bool, polygon_partial: bool, aws_partial: bool) -> str:
    if polygon_present and aws_present:
        return "both_present"
    if polygon_present:
        return "polygon_flat_file"
    if aws_present:
        return "generic_aws_only"
    if polygon_partial or aws_partial:
        return "ambiguous"
    return "missing"


def _safe_payload() -> dict[str, object]:
    env = os.environ
    polygon_present_names = _present_names(env, POLYGON_FLAT_FILE_CONFIG_NAMES)
    aws_present_names = _present_names(env, AWS_GENERIC_CONFIG_NAMES)
    polygon_missing_names = _missing_names(env, POLYGON_FLAT_FILE_CONFIG_NAMES)
    aws_missing_names = _missing_names(env, AWS_GENERIC_CONFIG_NAMES)

    polygon_flat_file_config_present = len(polygon_present_names) == len(POLYGON_FLAT_FILE_CONFIG_NAMES)
    generic_aws_s3_config_present = len(aws_present_names) == len(AWS_GENERIC_CONFIG_NAMES)
    polygon_partial = 0 < len(polygon_present_names) < len(POLYGON_FLAT_FILE_CONFIG_NAMES)
    aws_partial = 0 < len(aws_present_names) < len(AWS_GENERIC_CONFIG_NAMES)

    blockers = [
        "production handoff generation is not authorized",
        "no remote bucket listing or downloads are permitted in this preflight",
        "no vendor calls are permitted in this preflight",
    ]
    if not polygon_flat_file_config_present and generic_aws_s3_config_present:
        blockers.append("generic AWS S3 configuration is not sufficient for Polygon flat-file source access")
    if polygon_partial:
        blockers.append("Polygon flat-file configuration is incomplete")
    if aws_partial:
        blockers.append("generic AWS S3 configuration is incomplete")
    if not polygon_present_names and not aws_present_names:
        blockers.append("no recognizable Polygon flat-file or generic AWS S3 configuration names are present")

    config_classification = _config_classification(
        polygon_present=polygon_flat_file_config_present,
        aws_present=generic_aws_s3_config_present,
        polygon_partial=polygon_partial,
        aws_partial=aws_partial,
    )
    return {
        "preflight_only": True,
        "vendor_call_attempted": False,
        "remote_bucket_list_attempted": False,
        "download_attempted": False,
        "export_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "polygon_flat_file_config_present": polygon_flat_file_config_present,
        "generic_aws_s3_config_present": generic_aws_s3_config_present,
        "config_classification": config_classification,
        "polygon_required_config_names": list(POLYGON_FLAT_FILE_CONFIG_NAMES),
        "aws_generic_config_names": list(AWS_GENERIC_CONFIG_NAMES),
        "missing_polygon_config_names": polygon_missing_names,
        "credentials_printed": False,
        "endpoint_value_printed": False,
        "bucket_value_printed": False,
        "prefix_value_printed": False,
        "production_handoff_generation_authorized": False,
        "synthetic_forbidden": True,
        "fixture_only_forbidden": True,
        "blockers": blockers,
        "next_allowed_step": "explicit source selection review for Polygon flat-file credentials, not vendor access or production export",
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload()
    safe_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(safe_json + "\n", encoding="utf-8")
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
