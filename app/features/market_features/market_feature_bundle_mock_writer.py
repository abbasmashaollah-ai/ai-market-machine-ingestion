from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field


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


@dataclass(frozen=True, slots=True)
class MarketFeatureBundleMockWriteResult:
    writer_type: str
    dry_run_only: bool
    target_repo: str
    target_table: str
    idempotency_key: str | None
    would_write: bool
    write_status: str
    validation_errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    payload_summary: dict[str, object] = field(default_factory=dict)


class MarketFeatureBundleMockWriter:
    writer_type = "mock_market_feature_bundle_writer"
    target_repo = "ai-market-machine-data"
    target_table = "market_feature_bundle_snapshots"

    def write(self, payload: Mapping[str, object]) -> MarketFeatureBundleMockWriteResult:
        payload_copy = deepcopy(dict(payload))
        validation_errors: list[dict[str, object]] = []

        for field_name in REQUIRED_PAYLOAD_FIELDS:
            if field_name not in payload_copy:
                validation_errors.append({"field_name": field_name, "message": "field is required"})

        source_repo = payload_copy.get("source_repo")
        if source_repo != "ai-market-machine-ingestion":
            validation_errors.append({"field_name": "source_repo", "message": "source_repo must be ai-market-machine-ingestion"})

        if "full_bundle_payload" in payload_copy and not isinstance(payload_copy.get("full_bundle_payload"), Mapping):
            validation_errors.append({"field_name": "full_bundle_payload", "message": "field must be an object"})
        if "compact_summary" in payload_copy and not isinstance(payload_copy.get("compact_summary"), Mapping):
            validation_errors.append({"field_name": "compact_summary", "message": "field must be an object"})
        if "validation_status" in payload_copy and not isinstance(payload_copy.get("validation_status"), str):
            validation_errors.append({"field_name": "validation_status", "message": "field must be a string"})
        if "certification_status" in payload_copy and not isinstance(payload_copy.get("certification_status"), str):
            validation_errors.append({"field_name": "certification_status", "message": "field must be a string"})

        payload_text = str(payload_copy).lower()
        feature_snapshot_marker = "feature" + "snapshot"
        market_snapshot_marker = "market" + "snapshot"
        if feature_snapshot_marker in payload_text or market_snapshot_marker in payload_text:
            validation_errors.append({"field_name": "payload", "message": "snapshot language is not allowed"})

        payload_summary = {
            "observation_date": payload_copy.get("observation_date"),
            "universe": payload_copy.get("universe"),
            "schema_version": payload_copy.get("schema_version"),
            "dataset_version": payload_copy.get("dataset_version"),
            "validation_status": payload_copy.get("validation_status"),
            "certification_status": payload_copy.get("certification_status"),
            "raw_section_count": len(payload_copy.get("raw_sections") or []),
            "synthesized_section_count": len(payload_copy.get("synthesized_sections") or []),
            "total_warnings": payload_copy.get("total_warnings"),
            "safety_flag_count": len(payload_copy.get("safety_flags") or {}),
            "lineage_ref_count": len(payload_copy.get("lineage_refs") or []),
            "quality_result_ref_count": len(payload_copy.get("quality_result_refs") or []),
            "target_repo": self.target_repo,
            "target_table": self.target_table,
            "idempotency_key": payload_copy.get("idempotency_key"),
        }

        write_status = "MOCK_WRITE_READY" if not validation_errors else "MOCK_WRITE_REJECTED"
        would_write = not validation_errors
        return MarketFeatureBundleMockWriteResult(
            writer_type=self.writer_type,
            dry_run_only=True,
            target_repo=self.target_repo,
            target_table=self.target_table,
            idempotency_key=payload_copy.get("idempotency_key") if isinstance(payload_copy.get("idempotency_key"), str) else None,
            would_write=would_write,
            write_status=write_status,
            validation_errors=tuple(validation_errors),
            payload_summary=payload_summary,
        )


def build_market_feature_bundle_mock_write_result(payload: Mapping[str, object]) -> dict[str, object]:
    writer = MarketFeatureBundleMockWriter()
    result = writer.write(payload)
    return {
        "writer_type": result.writer_type,
        "dry_run_only": result.dry_run_only,
        "target_repo": result.target_repo,
        "target_table": result.target_table,
        "idempotency_key": result.idempotency_key,
        "would_write": result.would_write,
        "write_status": result.write_status,
        "validation_errors": [dict(error) for error in result.validation_errors],
        "payload_summary": dict(result.payload_summary),
    }
