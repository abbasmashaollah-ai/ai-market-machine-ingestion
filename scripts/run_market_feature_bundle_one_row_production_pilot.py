from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse
import sys

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload
from app.observability.market_feature_bundle_writer_observability import (
    build_market_feature_bundle_writer_observability_event,
    summarize_market_feature_bundle_writer_results,
)
from app.writers.market_feature_bundle_db_adapter import build_market_feature_bundle_session, validate_safe_test_database_url
from app.writers.market_feature_bundle_writer import MarketFeatureBundleWriter


APPROVAL_ENV = "AMM_PRODUCTION_PILOT_APPROVAL"
DATABASE_ENV = "AMM_PRODUCTION_PILOT_DATABASE_URL"
DATA_BASE_ENV = "AMM_PRODUCTION_PILOT_DATA_BASE_URL"
DATA_TOKEN_ENV = "AMM_PRODUCTION_PILOT_DATA_TOKEN"
APPROVAL_VALUE = "YES_APPROVED_ONE_ROW_ONLY"
PRESERVE_POLICY = "PRESERVE_FIRST_PRODUCTION_ROW"
TARGET_UNIVERSE = "SPY"
TARGET_DATASET_VERSION = "production_pilot.v1"
TARGET_SOURCE_RUN_ID = "production_pilot.v1"
TARGET_ROUTE = "/internal/read/market-feature-bundle/SPY"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the market feature bundle one-row production pilot.")
    parser.add_argument("--observation-date", default="2026-01-15", help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--timestamp", default=None, help="Optional ISO 8601 timestamp.")
    parser.add_argument("--output-file", default=None, help="Optional file path to write the JSON payload.")
    return parser


def _redact_database_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    host = parsed.hostname or "<unknown>"
    port = f":{parsed.port}" if parsed.port else ""
    database = parsed.path.lstrip("/") if parsed.path else "<unknown>"
    return f"{parsed.scheme}://<redacted>@{host}{port}/{database}"


def _load_required_env() -> dict[str, str]:
    approval = os.getenv(APPROVAL_ENV, "")
    database_url = os.getenv(DATABASE_ENV, "")
    data_base_url = os.getenv(DATA_BASE_ENV, "")
    data_token = os.getenv(DATA_TOKEN_ENV, "")
    missing = [name for name, value in ((APPROVAL_ENV, approval), (DATABASE_ENV, database_url), (DATA_BASE_ENV, data_base_url), (DATA_TOKEN_ENV, data_token)) if not value.strip()]
    if missing:
        raise RuntimeError(f"missing required production pilot env vars: {', '.join(missing)}")
    if approval.strip() != APPROVAL_VALUE:
        raise RuntimeError(f"invalid production pilot approval flag: {approval!r}")
    return {
        APPROVAL_ENV: approval.strip(),
        DATABASE_ENV: database_url.strip(),
        DATA_BASE_ENV: data_base_url.strip(),
        DATA_TOKEN_ENV: data_token.strip(),
    }


def _build_pilot_payload(*, observation_date: str, timestamp: str | None) -> dict[str, object]:
    bundle = run_market_feature_bundle_dry_run(observation_date=observation_date, timestamp=timestamp)
    return build_market_feature_bundle_producer_payload(
        bundle,
        observation_date=observation_date,
        generated_at=timestamp,
        universe=TARGET_UNIVERSE,
        dataset_version=TARGET_DATASET_VERSION,
        source_run_id=TARGET_SOURCE_RUN_ID,
    )


def _build_pilot_report(*, observation_date: str, timestamp: str | None) -> dict[str, object]:
    env = _load_required_env()
    payload = _build_pilot_payload(observation_date=observation_date, timestamp=timestamp)
    validate_safe_test_database_url(env[DATABASE_ENV])
    session = build_market_feature_bundle_session(env[DATABASE_ENV])
    writer = MarketFeatureBundleWriter(session, dry_run=False)
    write_result = writer.write_payload(payload)
    if write_result["write_status"] not in {"WRITE_ACCEPTED", "IDEMPOTENT_NOOP"}:
        raise RuntimeError(f"unexpected write_status for production pilot: {write_result['write_status']}")

    route_url = f"{env[DATA_BASE_ENV].rstrip('/')}{TARGET_ROUTE}"
    route_response = requests.get(route_url, headers={"X-Ops-Internal-Token": env[DATA_TOKEN_ENV]}, timeout=30)
    route_status = route_response.status_code
    route_payload = route_response.json() if hasattr(route_response, "json") else {}
    market_feature_bundle = route_payload.get("market_feature_bundle") or route_payload.get("data") or route_payload

    observability_event = build_market_feature_bundle_writer_observability_event(
        write_result,
        redacted_target=_redact_database_url(env[DATABASE_ENV]),
    )
    observability_summary = summarize_market_feature_bundle_writer_results([write_result])

    report = {
        "dry_run": False,
        "write_status": write_result["write_status"],
        "would_write": write_result["would_write"],
        "universe": payload["universe"],
        "dataset_version": payload["dataset_version"],
        "schema_version": payload["schema_version"],
        "idempotency_key_prefix": (payload.get("idempotency_key") or "")[:12],
        "validation_status": payload["validation_status"],
        "certification_status": payload["certification_status"],
        "target_table": write_result["target_table"],
        "target_repo": write_result["target_repo"],
        "preserve_policy": PRESERVE_POLICY,
        "observability_event": observability_event,
        "observability_summary": observability_summary,
        "production_target": _redact_database_url(env[DATABASE_ENV]),
        "data_route_base_url": env[DATA_BASE_ENV].rstrip("/"),
        "data_route_path": TARGET_ROUTE,
        "approval_state": APPROVAL_VALUE,
        "route_status": route_status,
        "route_read_back": {
            "idempotency_key": market_feature_bundle.get("idempotency_key") if isinstance(market_feature_bundle, dict) else None,
            "universe": market_feature_bundle.get("universe") if isinstance(market_feature_bundle, dict) else None,
            "schema_version": market_feature_bundle.get("schema_version") if isinstance(market_feature_bundle, dict) else None,
            "dataset_version": market_feature_bundle.get("dataset_version") if isinstance(market_feature_bundle, dict) else None,
            "compact_summary": market_feature_bundle.get("compact_summary") if isinstance(market_feature_bundle, dict) else None,
            "full_bundle_payload": market_feature_bundle.get("full_bundle_payload") if isinstance(market_feature_bundle, dict) else None,
            "validation_status": market_feature_bundle.get("validation_status") if isinstance(market_feature_bundle, dict) else None,
            "certification_status": market_feature_bundle.get("certification_status") if isinstance(market_feature_bundle, dict) else None,
            "lineage_refs": market_feature_bundle.get("lineage_refs") if isinstance(market_feature_bundle, dict) else None,
            "quality_result_refs": market_feature_bundle.get("quality_result_refs") if isinstance(market_feature_bundle, dict) else None,
        },
    }
    return report


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = _build_pilot_report(observation_date=args.observation_date, timestamp=args.timestamp)
    except Exception as exc:
        sys.stderr.write(str(exc) + "\n")
        return 1

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
