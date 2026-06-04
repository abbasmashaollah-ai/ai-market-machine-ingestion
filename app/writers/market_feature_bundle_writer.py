from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

REQUIRED_PAYLOAD_FIELDS = (
    "observation_date",
    "generated_at",
    "universe",
    "schema_version",
    "dataset_version",
    "idempotency_key",
    "raw_sections",
    "synthesized_sections",
    "section_record_counts",
    "section_labels",
    "compact_summary",
    "full_bundle_payload",
    "validation_status",
    "validation_errors",
    "validation_warnings",
    "total_warnings",
    "safety_flags",
    "rejected_counts",
    "certification_status",
    "source_repo",
    "source_run_id",
    "input_dataset_versions",
    "lineage_refs",
    "quality_result_refs",
)

TARGET_REPO = "ai-market-machine-data"
TARGET_TABLE = "market_feature_bundle_snapshots"


class MarketFeatureBundleWriter:
    def __init__(self, session, *, dry_run: bool = True):
        self._session = session
        self._dry_run = bool(dry_run)

    def _validate_payload(self, payload: Mapping[str, object]) -> list[dict[str, object]]:
        errors: list[dict[str, object]] = []

        for field_name in REQUIRED_PAYLOAD_FIELDS:
            if field_name not in payload:
                errors.append({"field_name": field_name, "message": "field is required"})

        if payload.get("source_repo") != "ai-market-machine-ingestion":
            errors.append({"field_name": "source_repo", "message": "source_repo must be ai-market-machine-ingestion"})

        for field_name in ("validation_status", "certification_status", "full_bundle_payload", "compact_summary", "idempotency_key"):
            value = payload.get(field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append({"field_name": field_name, "message": "field is required"})

        if "full_bundle_payload" in payload and not isinstance(payload.get("full_bundle_payload"), Mapping):
            errors.append({"field_name": "full_bundle_payload", "message": "field must be an object"})
        if "compact_summary" in payload and not isinstance(payload.get("compact_summary"), Mapping):
            errors.append({"field_name": "compact_summary", "message": "field must be an object"})

        return errors

    def _grain(self, payload: Mapping[str, object]) -> dict[str, object]:
        return {
            "observation_date": payload.get("observation_date"),
            "universe": payload.get("universe"),
            "schema_version": payload.get("schema_version"),
            "dataset_version": payload.get("dataset_version"),
        }

    def _payload_summary(self, payload: Mapping[str, object]) -> dict[str, object]:
        return {
            "observation_date": payload.get("observation_date"),
            "universe": payload.get("universe"),
            "schema_version": payload.get("schema_version"),
            "dataset_version": payload.get("dataset_version"),
            "validation_status": payload.get("validation_status"),
            "certification_status": payload.get("certification_status"),
            "total_warnings": payload.get("total_warnings"),
            "raw_section_count": len(payload.get("raw_sections") or []),
            "synthesized_section_count": len(payload.get("synthesized_sections") or []),
            "lineage_ref_count": len(payload.get("lineage_refs") or []),
            "quality_result_ref_count": len(payload.get("quality_result_refs") or []),
        }

    def write_payload(self, payload: dict) -> dict:
        payload_copy = deepcopy(dict(payload or {}))
        validation_errors = self._validate_payload(payload_copy)
        grain = self._grain(payload_copy)
        idempotency_key = payload_copy.get("idempotency_key") if isinstance(payload_copy.get("idempotency_key"), str) else None
        payload_summary = self._payload_summary(payload_copy)

        if validation_errors:
            return {
                "writer_type": "market_feature_bundle_writer",
                "dry_run": self._dry_run,
                "target_repo": TARGET_REPO,
                "target_table": TARGET_TABLE,
                "idempotency_key": idempotency_key,
                "grain": grain,
                "would_write": False,
                "write_status": "REJECTED",
                "validation_errors": validation_errors,
                "conflict_status": "VALIDATION_FAILED",
                "payload_summary": payload_summary,
            }

        if self._dry_run:
            return {
                "writer_type": "market_feature_bundle_writer",
                "dry_run": self._dry_run,
                "target_repo": TARGET_REPO,
                "target_table": TARGET_TABLE,
                "idempotency_key": idempotency_key,
                "grain": grain,
                "would_write": True,
                "write_status": "DRY_RUN_READY",
                "validation_errors": [],
                "conflict_status": "NONE",
                "payload_summary": payload_summary,
            }

        session = self._session

        try:
            if hasattr(session, "existing_by_idempotency_key"):
                existing = session.existing_by_idempotency_key(idempotency_key)
                if existing is not None:
                    return {
                        "writer_type": "market_feature_bundle_writer",
                        "dry_run": self._dry_run,
                        "target_repo": TARGET_REPO,
                        "target_table": TARGET_TABLE,
                        "idempotency_key": idempotency_key,
                        "grain": grain,
                        "would_write": False,
                        "write_status": "IDEMPOTENT_NOOP",
                        "validation_errors": [],
                        "conflict_status": "ALREADY_EXISTS",
                        "payload_summary": payload_summary,
                    }

            if hasattr(session, "existing_by_grain"):
                existing_grain = session.existing_by_grain(grain)
                if existing_grain is not None:
                    existing_idempotency_key = None
                    if isinstance(existing_grain, Mapping):
                        existing_idempotency_key = existing_grain.get("idempotency_key") if isinstance(existing_grain.get("idempotency_key"), str) else None
                    if existing_idempotency_key and existing_idempotency_key != idempotency_key:
                        return {
                            "writer_type": "market_feature_bundle_writer",
                            "dry_run": self._dry_run,
                            "target_repo": TARGET_REPO,
                            "target_table": TARGET_TABLE,
                            "idempotency_key": idempotency_key,
                            "grain": grain,
                            "would_write": False,
                            "write_status": "CONFLICT",
                            "validation_errors": [],
                            "conflict_status": "GRAIN_CONFLICT",
                            "payload_summary": payload_summary,
                        }

            if hasattr(session, "add"):
                session.add(deepcopy(payload_copy))
            if hasattr(session, "merge"):
                session.merge(deepcopy(payload_copy))
            if hasattr(session, "commit"):
                session.commit()
            return {
                "writer_type": "market_feature_bundle_writer",
                "dry_run": self._dry_run,
                "target_repo": TARGET_REPO,
                "target_table": TARGET_TABLE,
                "idempotency_key": idempotency_key,
                "grain": grain,
                "would_write": True,
                "write_status": "WRITE_ACCEPTED",
                "validation_errors": [],
                "conflict_status": "NONE",
                "payload_summary": payload_summary,
            }
        except Exception as exc:
            if hasattr(session, "rollback"):
                session.rollback()
            return {
                "writer_type": "market_feature_bundle_writer",
                "dry_run": self._dry_run,
                "target_repo": TARGET_REPO,
                "target_table": TARGET_TABLE,
                "idempotency_key": idempotency_key,
                "grain": grain,
                "would_write": False,
                "write_status": "WRITE_FAILED",
                "validation_errors": [{"field_name": "session", "message": str(exc)}],
                "conflict_status": "SESSION_FAILURE",
                "payload_summary": payload_summary,
            }

