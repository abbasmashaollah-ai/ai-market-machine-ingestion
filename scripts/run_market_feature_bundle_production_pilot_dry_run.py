from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload
from app.observability.market_feature_bundle_writer_observability import build_market_feature_bundle_writer_observability_event
from app.writers.market_feature_bundle_writer import MarketFeatureBundleWriter


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the market feature bundle production pilot dry run and print JSON output.")
    parser.add_argument("--observation-date", default="2026-01-15", help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--timestamp", default=None, help="Optional ISO 8601 timestamp.")
    parser.add_argument("--output-file", default=None, help="Optional file path to write the JSON payload.")
    return parser


def _build_dry_run_report(*, observation_date: str, timestamp: str | None) -> dict[str, object]:
    bundle = run_market_feature_bundle_dry_run(observation_date=observation_date, timestamp=timestamp)
    payload = build_market_feature_bundle_producer_payload(
        bundle,
        observation_date=observation_date,
        generated_at=timestamp,
        universe="SPY",
        dataset_version="production_pilot.v1",
        source_run_id="production_pilot_dry_run",
    )
    writer = MarketFeatureBundleWriter(session=None, dry_run=True)
    writer_result = writer.write_payload(payload)
    event = build_market_feature_bundle_writer_observability_event(
        writer_result,
        redacted_target="postgresql://<redacted>@production-target/redacted",
    )
    return {
        "dry_run": True,
        "would_write": writer_result["would_write"],
        "write_status": writer_result["write_status"],
        "universe": payload["universe"],
        "dataset_version": payload["dataset_version"],
        "schema_version": payload["schema_version"],
        "idempotency_key_prefix": (payload.get("idempotency_key") or "")[:12],
        "validation_status": payload["validation_status"],
        "certification_status": payload["certification_status"],
        "target_table": writer_result["target_table"],
        "target_repo": writer_result["target_repo"],
        "preserve_policy": "PRESERVE_FIRST_PRODUCTION_ROW",
        "scheduler_enabled": False,
        "backfill_enabled": False,
        "ai_machine_touched": False,
        "observability_event": event,
    }


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    report = _build_dry_run_report(observation_date=args.observation_date, timestamp=args.timestamp)
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
