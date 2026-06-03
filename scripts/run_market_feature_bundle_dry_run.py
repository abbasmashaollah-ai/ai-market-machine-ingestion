from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_features.market_feature_bundle_validator import validate_market_feature_bundle


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the market feature bundle dry run and print JSON output.")
    parser.add_argument("--observation-date", default=None, help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--timestamp", default=None, help="Optional ISO 8601 timestamp.")
    parser.add_argument("--output-file", default=None, help="Optional file path to write the JSON payload.")
    parser.add_argument("--summary-only", action="store_true", help="Print the compact evidence summary instead of the full bundle.")
    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    observation_date = args.observation_date or "2026-01-15"
    bundle = run_market_feature_bundle_dry_run(observation_date=observation_date, timestamp=args.timestamp)
    validation_result = validate_market_feature_bundle(bundle)
    if not validation_result.is_valid:
        error_payload = {
            "is_valid": False,
            "errors": [{"field_name": error.field_name, "message": error.message} for error in validation_result.errors],
            "warnings": list(validation_result.warnings),
        }
        error_json = json.dumps(error_payload, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write(error_json)
        sys.stdout.write("\n")
        return 1
    payload_object = build_market_feature_bundle_summary(bundle) if args.summary_only else bundle
    payload = json.dumps(payload_object, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
