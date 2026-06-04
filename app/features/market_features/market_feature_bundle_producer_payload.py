from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import date, datetime, timezone
from typing import Any

from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_features.market_feature_bundle_validator import validate_market_feature_bundle


RAW_SECTION_NAMES = (
    "prices",
    "breadth",
    "sector_rotation",
    "cross_asset",
    "liquidity_rates",
    "volatility",
    "event_calendar",
    "news_sentiment",
    "earnings",
    "fundamentals",
    "flows_positioning",
    "options",
)

SYNTHESIZED_SECTION_NAMES = (
    "macro_liquidity",
    "market_risk",
    "market_regime",
)


def _normalize_datetime(value: str | date | datetime | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _stable_checksum(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _section_count(section: object) -> int:
    if isinstance(section, Mapping):
        for key in ("reports", "reports_by_symbol", "earnings_regime_labels_by_symbol", "fundamental_quality_labels_by_symbol", "options_regime_labels_by_symbol"):
            nested = section.get(key)
            if isinstance(nested, Mapping):
                return len(nested)
            if isinstance(nested, list):
                return len(nested)
        for key in ("accepted_count", "rejected_count", "accepted_observation_count", "accepted_summary_count", "rejected_observation_count", "rejected_summary_count"):
            value = section.get(key)
            if isinstance(value, int):
                return value
    return 0


def _section_label(section: object, label_keys: tuple[str, ...]) -> str | None:
    if not isinstance(section, Mapping):
        return None
    for key in label_keys:
        value = section.get(key)
        if isinstance(value, str) and value.strip():
            return value
    report = section.get("report")
    if isinstance(report, Mapping):
        for key in label_keys:
            value = report.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return None


def _section_state(bundle: Mapping[str, object], section_name: str) -> str | None:
    section = bundle.get(section_name)
    if section_name == "breadth":
        return _section_label(section, ("participation_label",))
    if section_name == "sector_rotation":
        return _section_label(section, ("descriptive_rotation_state",))
    if section_name == "cross_asset":
        return _section_label(section, ("descriptive_intermarket_state",))
    if section_name == "liquidity_rates":
        return _section_label(section, ("liquidity_regime_label",))
    if section_name == "volatility":
        return _section_label(section, ("volatility_regime_label",))
    if section_name == "event_calendar":
        return _section_label(section, ("event_risk_label",))
    if section_name == "news_sentiment":
        return _section_label(section, ("sentiment_regime_label",))
    if section_name == "earnings":
        return _section_label(section, ("earnings_regime_label",))
    if section_name == "fundamentals":
        return _section_label(section, ("fundamental_quality_label",))
    if section_name == "flows_positioning":
        return _section_label(section, ("flow_regime_label",))
    if section_name == "options":
        return _section_label(section, ("options_regime_label",))
    if section_name == "macro_liquidity":
        return _section_label(section, ("macro_liquidity_label",))
    if section_name == "market_risk":
        return _section_label(section, ("market_risk_label",))
    if section_name == "market_regime":
        return _section_label(section, ("market_regime_label",))
    return None


def _payload_without_idempotency(payload: Mapping[str, object]) -> dict[str, object]:
    safe_payload = dict(payload)
    safe_payload.pop("idempotency_key", None)
    return safe_payload


def build_market_feature_bundle_producer_payload(
    bundle: dict,
    *,
    observation_date: str | date | None = None,
    generated_at: str | datetime | None = None,
    universe: str = "SPY",
    schema_version: str = "market_feature_bundle.v1",
    dataset_version: str = "fixture.v1",
    source_run_id: str | None = None,
    input_dataset_versions: dict | None = None,
    lineage_refs: list | None = None,
    quality_result_refs: list | None = None,
) -> dict:
    bundle_payload = dict(bundle or {})
    summary = build_market_feature_bundle_summary(bundle_payload)
    validation_result = validate_market_feature_bundle(bundle_payload)
    normalized_observation_date = _normalize_datetime(observation_date or bundle_payload.get("observation_date"))
    normalized_generated_at = _normalize_datetime(generated_at) or _normalize_datetime(bundle_payload.get("generated_at"))

    raw_sections = [name for name in RAW_SECTION_NAMES if name in bundle_payload]
    synthesized_sections = [name for name in SYNTHESIZED_SECTION_NAMES if name in bundle_payload]

    section_labels = {name: _section_state(bundle_payload, name) for name in raw_sections + synthesized_sections}
    section_record_counts = {name: _section_count(bundle_payload.get(name)) for name in raw_sections + synthesized_sections}

    validation_status = "PASS" if validation_result.is_valid and int(summary.get("total_warnings") or 0) == 0 else ("WARN" if validation_result.is_valid else "FAIL")
    safety_flags = dict(summary.get("safety_flags") or {})
    certification_status = "CERTIFIED" if validation_status == "PASS" and all(bool(safety_flags.get(flag)) for flag in ("no_db_writes", "no_vendor_calls", "no_live_api_calls", "no_scheduler_activation")) else "UNCERTIFIED"

    payload: dict[str, object] = {
        "observation_date": normalized_observation_date,
        "generated_at": normalized_generated_at,
        "universe": universe,
        "schema_version": schema_version,
        "dataset_version": dataset_version,
        "raw_sections": raw_sections,
        "synthesized_sections": synthesized_sections,
        "section_record_counts": section_record_counts,
        "section_labels": section_labels,
        "compact_summary": summary,
        "full_bundle_payload": bundle_payload,
        "validation_status": validation_status,
        "validation_errors": [
            {"field_name": error.field_name, "message": error.message}
            for error in validation_result.errors
        ],
        "validation_warnings": list(validation_result.warnings),
        "total_warnings": int(summary.get("total_warnings") or 0),
        "safety_flags": safety_flags,
        "rejected_counts": dict(summary.get("rejected_counts_by_section") or {}),
        "certification_status": certification_status,
        "source_repo": "ai-market-machine-ingestion",
        "source_run_id": source_run_id,
        "input_dataset_versions": dict(input_dataset_versions or {}),
        "lineage_refs": list(lineage_refs or []),
        "quality_result_refs": list(quality_result_refs or []),
    }

    checksum_payload = {
        "observation_date": payload["observation_date"],
        "generated_at": payload["generated_at"],
        "universe": payload["universe"],
        "schema_version": payload["schema_version"],
        "dataset_version": payload["dataset_version"],
        "compact_summary": payload["compact_summary"],
        "full_bundle_payload": payload["full_bundle_payload"],
        "validation_status": payload["validation_status"],
        "validation_errors": payload["validation_errors"],
        "validation_warnings": payload["validation_warnings"],
        "total_warnings": payload["total_warnings"],
        "safety_flags": payload["safety_flags"],
        "rejected_counts": payload["rejected_counts"],
        "certification_status": payload["certification_status"],
        "source_repo": payload["source_repo"],
        "source_run_id": payload["source_run_id"],
        "input_dataset_versions": payload["input_dataset_versions"],
        "lineage_refs": payload["lineage_refs"],
        "quality_result_refs": payload["quality_result_refs"],
        "raw_sections": payload["raw_sections"],
        "synthesized_sections": payload["synthesized_sections"],
        "section_record_counts": payload["section_record_counts"],
        "section_labels": payload["section_labels"],
    }
    payload["idempotency_key"] = hashlib.sha256(_stable_json(checksum_payload).encode("utf-8")).hexdigest()
    return payload

