from __future__ import annotations

import json
import re
from pathlib import Path


EXPECTED_OBSERVATION_DATE = "2026-01-15"
EXPECTED_SCHEMA_VERSION = "market_feature_bundle.v1"
EXPECTED_DATASET_VERSION = "production_pilot.fixture_dry_run.v1"
EXPECTED_SOURCE_REPO = "ai-market-machine-ingestion"
EXPECTED_SOURCE_RUN_ID = "fixture_dry_run.v1"
ALLOWED_CERTIFICATION_STATUSES = {"FIXTURE_CERTIFIED", "DRY_RUN_CERTIFIED"}


def load_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _universe_from_filename(path: Path) -> str:
    stem = path.stem.lower()
    if "qqq" in stem:
        return "QQQ"
    if "iwm" in stem:
        return "IWM"
    if "dia" in stem:
        return "DIA"
    raise ValueError(f"Cannot infer universe from filename: {path.name}")


def _contains_forbidden_secret(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in ("secret", "token", "credential", "apikey", "api_key", "raw_provider"))


def validate_fixture_payload(payload: dict, *, path: Path | None = None) -> list[str]:
    errors: list[str] = []
    universe = payload.get("universe")
    if path is not None:
        expected_universe = _universe_from_filename(path)
        if universe != expected_universe:
            errors.append("universe mismatch")
    if universe not in {"QQQ", "IWM", "DIA"}:
        errors.append("missing or invalid universe")
    if payload.get("observation_date") != EXPECTED_OBSERVATION_DATE:
        errors.append("invalid observation_date")
    if payload.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append("invalid schema_version")
    if payload.get("dataset_version") != EXPECTED_DATASET_VERSION:
        errors.append("invalid dataset_version")
    if payload.get("validation_status") != "PASS":
        errors.append("invalid validation_status")
    if payload.get("coverage_status") != "COMPLETE":
        errors.append("invalid coverage_status")
    if payload.get("quality_status") != "PASS":
        errors.append("invalid quality_status")
    certification_status = payload.get("certification_status")
    if certification_status == "CERTIFIED":
        errors.append("production certification_status forbidden")
    if certification_status not in ALLOWED_CERTIFICATION_STATUSES:
        errors.append("invalid certification_status")
    if payload.get("source_repo") != EXPECTED_SOURCE_REPO:
        errors.append("invalid source_repo")
    if payload.get("source_run_id") != EXPECTED_SOURCE_RUN_ID:
        errors.append("invalid source_run_id")
    idempotency_key = payload.get("idempotency_key")
    if not isinstance(idempotency_key, str) or "fixture_dry_run" not in idempotency_key or not re.search(r"[a-z0-9]+\.[a-z0-9_-]+\.2026-01-15\.v1$", idempotency_key):
        errors.append("invalid idempotency_key")
    if not payload.get("lineage_refs") or not payload.get("quality_result_refs"):
        errors.append("missing lineage or quality refs")
    if _contains_forbidden_secret(json.dumps(payload, sort_keys=True)):
        errors.append("forbidden secret material")
    if payload.get("validation_errors") not in ([], None):
        errors.append("validation_errors must be empty")
    if "fixture-only" not in str(payload.get("note", "")).lower() or "not production evidence" not in str(payload.get("note", "")).lower():
        errors.append("note missing fixture disclaimer")
    if not payload.get("raw_sections") or not payload.get("synthesized_sections"):
        errors.append("missing sections")
    if payload.get("exposes_data_api") or payload.get("production_route"):
        errors.append("must not expose externally")
    return errors


def validate_fixture_file(path: Path) -> list[str]:
    payload = load_fixture(path)
    return validate_fixture_payload(payload, path=path)
