"""Breadth observations JSONL handoff builder.

This module reuses the existing breadth observation builder, validator, and
mock writer patterns to produce contract-aligned JSONL handoff records without
adding production side effects.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.features.breadth.breadth_validator import BreadthValidationError, validate_breadth_observation

DEFAULT_SCHEMA_VERSION = "breadth_observations_jsonl_v1"
DEFAULT_OUTPUT_PATH = Path("outputs") / "handoff" / "breadth" / "breadth_observations.jsonl"

_DERIVED_FIELDS = (
    "advance_decline_ratio",
    "advance_decline_line",
    "breadth_score",
    "participation_score",
    "participation_label",
    "breadth_thrust",
    "mcclellan_oscillator",
    "ad_line",
    "sector_participation",
    "sector_rotation",
    "buy_signal",
    "sell_signal",
    "signal",
    "regime",
)


@dataclass(frozen=True, slots=True)
class BreadthObservationsHandoffRecordResult:
    accepted: bool
    record: dict[str, Any] | None
    rejection_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    idempotency_key: str | None
    idempotency_components: dict[str, str] | None


@dataclass(frozen=True, slots=True)
class BreadthObservationsHandoffWriteResult:
    records_received: int
    records_written: int
    records_rejected: int
    rejection_reasons: tuple[dict[str, Any], ...]
    output_path: str
    schema_version: str
    source_vendor: str
    source_dataset: str
    source_sha256: str
    generated_at: str
    quarantine_path: str | None
    idempotency_keys: tuple[str, ...] = field(default_factory=tuple)
    lineage_summary: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_vendor_calls: bool = True
    no_db_writes: bool = True
    no_scheduler_activation: bool = True


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _sha256_text(*parts: str | None) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _non_negative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _non_negative_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) >= 0.0


def _coerce_metadata(observation: Mapping[str, Any]) -> dict[str, Any]:
    metadata = dict(observation.get("metadata") or {})
    for field_name in _DERIVED_FIELDS:
        if field_name in observation and observation.get(field_name) is not None:
            metadata.setdefault(field_name, observation.get(field_name))
    for field_name in ("quality_status", "certification_status", "freshness_status", "lineage", "evidence", "source"):
        if field_name in observation and observation.get(field_name) is not None:
            metadata.setdefault(field_name, observation.get(field_name))
    return metadata


def _explicit_percent_field(observation: Mapping[str, Any], source_field: str, target_field: str) -> tuple[str, Any] | None:
    value = observation.get(target_field)
    if value is not None:
        return target_field, value
    legacy_value = observation.get(source_field)
    if legacy_value is not None:
        return target_field, legacy_value
    return None


def validate_breadth_observation_handoff_record(record: Mapping[str, Any]) -> BreadthObservationsHandoffRecordResult:
    warnings: list[str] = []
    rejection_reasons: list[str] = []
    payload = dict(record)

    required_fields = (
        "observation_date",
        "universe_key",
        "source_vendor",
        "source_dataset",
        "source_sha256",
        "observed_symbol_count",
        "advancing_count",
        "declining_count",
        "unchanged_count",
        "advancing_volume",
        "declining_volume",
        "new_high_count",
        "new_low_count",
        "generated_at",
        "schema_version",
        "metadata",
    )
    for field_name in required_fields:
        if field_name not in payload:
            rejection_reasons.append(f"{field_name} is required")

    universe_key = _safe_text(payload.get("universe_key"))
    if not universe_key:
        rejection_reasons.append("universe_key must be a non-empty string")
    if not _safe_text(payload.get("source_vendor")):
        rejection_reasons.append("source_vendor must be a non-empty string")
    if not _safe_text(payload.get("source_dataset")):
        rejection_reasons.append("source_dataset must be a non-empty string")
    if not _safe_text(payload.get("source_sha256")):
        rejection_reasons.append("source_sha256 must be a non-empty string")
    if not _safe_text(payload.get("generated_at")):
        rejection_reasons.append("generated_at must be a non-empty string")
    if not _safe_text(payload.get("schema_version")):
        rejection_reasons.append("schema_version must be a non-empty string")
    if not isinstance(payload.get("metadata"), dict):
        rejection_reasons.append("metadata must be an object")

    for field_name in ("observed_symbol_count", "advancing_count", "declining_count", "unchanged_count", "new_high_count", "new_low_count"):
        value = payload.get(field_name)
        if not _non_negative_int(value):
            rejection_reasons.append(f"{field_name} must be a non-negative integer")

    for field_name in ("advancing_volume", "declining_volume", "unchanged_volume"):
        value = payload.get(field_name)
        if value is not None and not _non_negative_number(value):
            rejection_reasons.append(f"{field_name} must be a non-negative number when present")

    for field_name in ("percent_above_20d_ma", "percent_above_50d_ma", "percent_above_100d_ma", "percent_above_150d_ma", "percent_above_200d_ma"):
        value = payload.get(field_name)
        if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool)):
            rejection_reasons.append(f"{field_name} must be numeric when present")

    observed_count = payload.get("observed_symbol_count")
    advancing_count = payload.get("advancing_count")
    declining_count = payload.get("declining_count")
    unchanged_count = payload.get("unchanged_count")
    if all(_non_negative_int(v) for v in (observed_count, advancing_count, declining_count, unchanged_count)):
        if int(observed_count) != int(advancing_count) + int(declining_count) + int(unchanged_count):
            rejection_reasons.append("observed_symbol_count must equal advancing_count + declining_count + unchanged_count")

    if payload.get("advance_decline_line") is not None or payload.get("breadth_score") is not None or payload.get("participation_score") is not None:
        warnings.append("derived breadth metrics retained only in metadata when present")

    if rejection_reasons:
        return BreadthObservationsHandoffRecordResult(
            accepted=False,
            record=None,
            rejection_reasons=tuple(dict.fromkeys(rejection_reasons)),
            warnings=tuple(warnings),
            idempotency_key=None,
            idempotency_components=None,
        )

    idempotency_components = {
        "source_vendor": str(payload.get("source_vendor") or ""),
        "source_dataset": str(payload.get("source_dataset") or ""),
        "source_sha256": str(payload.get("source_sha256") or ""),
        "observation_date": str(payload.get("observation_date") or ""),
        "universe_key": str(payload.get("universe_key") or ""),
        "schema_version": str(payload.get("schema_version") or ""),
    }
    idempotency_key = _sha256_text(
        idempotency_components["source_vendor"],
        idempotency_components["source_dataset"],
        idempotency_components["source_sha256"],
        idempotency_components["observation_date"],
        idempotency_components["universe_key"],
        idempotency_components["schema_version"],
    )
    return BreadthObservationsHandoffRecordResult(
        accepted=True,
        record=dict(payload),
        rejection_reasons=tuple(),
        warnings=tuple(warnings),
        idempotency_key=idempotency_key,
        idempotency_components=idempotency_components,
    )


def _canonicalize_record(
    observation: Mapping[str, Any],
    *,
    source_vendor: str,
    source_dataset: str,
    source_sha256: str,
    schema_version: str,
    generated_at: str,
) -> dict[str, Any]:
    universe_key = _safe_text(observation.get("universe_key")) or _safe_text(observation.get("universe"))
    if universe_key is None:
        universe_key = ""
    generated = _safe_text(observation.get("generated_at")) or generated_at
    metadata = _coerce_metadata(observation)
    lineage = metadata.get("lineage")
    if not isinstance(lineage, dict):
        lineage = {}
    lineage.setdefault("source_vendor", source_vendor)
    lineage.setdefault("source_dataset", source_dataset)
    lineage.setdefault("source_sha256", source_sha256)
    lineage.setdefault("source", _safe_text(observation.get("source")))
    lineage.setdefault("universe", _safe_text(observation.get("universe")))

    record: dict[str, Any] = {
        "observation_date": observation.get("observation_date"),
        "universe_key": universe_key,
        "universe_name": _safe_text(observation.get("universe_name")),
        "source_vendor": _safe_text(observation.get("source_vendor")) or source_vendor,
        "source_dataset": _safe_text(observation.get("source_dataset")) or source_dataset,
        "source_file": _safe_text(observation.get("source_file")),
        "source_uri": _safe_text(observation.get("source_uri")),
        "source_sha256": _safe_text(observation.get("source_sha256")) or source_sha256,
        "observed_symbol_count": observation.get("observed_symbol_count")
        if observation.get("observed_symbol_count") is not None
        else int(observation.get("advancers", 0)) + int(observation.get("decliners", 0)) + int(observation.get("unchanged", 0)),
        "advancing_count": observation.get("advancing_count") if observation.get("advancing_count") is not None else observation.get("advancers"),
        "declining_count": observation.get("declining_count") if observation.get("declining_count") is not None else observation.get("decliners"),
        "unchanged_count": observation.get("unchanged_count") if observation.get("unchanged_count") is not None else observation.get("unchanged"),
        "advancing_volume": observation.get("advancing_volume"),
        "declining_volume": observation.get("declining_volume"),
        "unchanged_volume": observation.get("unchanged_volume"),
        "new_high_count": observation.get("new_high_count") if observation.get("new_high_count") is not None else observation.get("new_highs"),
        "new_low_count": observation.get("new_low_count") if observation.get("new_low_count") is not None else observation.get("new_lows"),
        "percent_above_20d_ma": None,
        "percent_above_50d_ma": None,
        "percent_above_100d_ma": observation.get("percent_above_100d_ma"),
        "percent_above_150d_ma": observation.get("percent_above_150d_ma"),
        "percent_above_200d_ma": None,
        "generated_at": generated,
        "schema_version": _safe_text(observation.get("schema_version")) or schema_version,
        "metadata": metadata,
    }
    percent_20 = _explicit_percent_field(observation, "percent_above_20d", "percent_above_20d_ma")
    if percent_20 is not None:
        record[percent_20[0]] = percent_20[1]
    percent_50 = _explicit_percent_field(observation, "percent_above_50d", "percent_above_50d_ma")
    if percent_50 is not None:
        record[percent_50[0]] = percent_50[1]
    percent_200 = _explicit_percent_field(observation, "percent_above_200d", "percent_above_200d_ma")
    if percent_200 is not None:
        record[percent_200[0]] = percent_200[1]
    if record["percent_above_100d_ma"] is None and observation.get("percent_above_100d") is not None:
        record["percent_above_100d_ma"] = observation.get("percent_above_100d")

    # preserve trace/debug hints only in metadata; never promote them canonically
    metadata.setdefault("trace", {})
    trace = metadata.get("trace")
    if isinstance(trace, dict):
        for field_name in _DERIVED_FIELDS:
            if observation.get(field_name) is not None:
                trace.setdefault(field_name, observation.get(field_name))
    record["metadata"] = metadata
    return record


def build_breadth_observations_handoff_records(
    observations: Sequence[Mapping[str, Any]],
    *,
    source_vendor: str,
    source_dataset: str,
    source_sha256: str,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    generated_at: str | None = None,
) -> tuple[BreadthObservationsHandoffRecordResult, ...]:
    generated_at_value = generated_at or _utc_now()
    results: list[BreadthObservationsHandoffRecordResult] = []
    for observation in observations:
        canonical_record = _canonicalize_record(
            observation,
            source_vendor=source_vendor,
            source_dataset=source_dataset,
            source_sha256=source_sha256,
            schema_version=schema_version,
            generated_at=generated_at_value,
        )
        result = validate_breadth_observation_handoff_record(canonical_record)
        if result.accepted and result.record is not None:
            results.append(result)
            continue
        results.append(result)
    return tuple(results)


def write_breadth_observations_handoff_jsonl(
    observations: Sequence[Mapping[str, Any]],
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    *,
    source_vendor: str,
    source_dataset: str,
    source_sha256: str,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    generated_at: str | None = None,
    quarantine_path: str | Path | None = None,
) -> BreadthObservationsHandoffWriteResult:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    quarantine_target = Path(quarantine_path) if quarantine_path is not None else None
    if quarantine_target is not None:
        quarantine_target.parent.mkdir(parents=True, exist_ok=True)

    generated_at_value = generated_at or _utc_now()
    results = build_breadth_observations_handoff_records(
        observations,
        source_vendor=source_vendor,
        source_dataset=source_dataset,
        source_sha256=source_sha256,
        schema_version=schema_version,
        generated_at=generated_at_value,
    )

    written_records: list[dict[str, Any]] = []
    rejection_reasons: list[dict[str, Any]] = []
    quarantined_records: list[dict[str, Any]] = []
    idempotency_keys: list[str] = []
    warnings: list[str] = []

    for index, result in enumerate(results):
        warnings.extend(result.warnings)
        if result.accepted and result.record is not None:
            written_records.append(result.record)
            if result.idempotency_key:
                idempotency_keys.append(result.idempotency_key)
        else:
            rejection = {
                "index": index,
                "rejection_reasons": list(result.rejection_reasons),
                "warnings": list(result.warnings),
                "record": _json_safe(dict(observations[index])),
            }
            rejection_reasons.append(rejection)
            quarantined_records.append(rejection)

    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in written_records:
            handle.write(json.dumps(_json_safe(record), ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    quarantine_written = False
    if quarantine_target is not None and quarantined_records:
        quarantine_written = True
        with quarantine_target.open("w", encoding="utf-8", newline="\n") as handle:
            for record in quarantined_records:
                handle.write(json.dumps(_json_safe(record), ensure_ascii=False, sort_keys=True))
                handle.write("\n")

    lineage_summary = {
        "source_vendor": source_vendor,
        "source_dataset": source_dataset,
        "source_sha256": source_sha256,
        "schema_version": schema_version,
        "generated_at": generated_at_value,
        "quarantine_written": quarantine_written,
    }
    return BreadthObservationsHandoffWriteResult(
        records_received=len(observations),
        records_written=len(written_records),
        records_rejected=len(rejection_reasons),
        rejection_reasons=tuple(rejection_reasons),
        output_path=str(output_path),
        schema_version=schema_version,
        source_vendor=source_vendor,
        source_dataset=source_dataset,
        source_sha256=source_sha256,
        generated_at=generated_at_value,
        quarantine_path=str(quarantine_target) if quarantine_target is not None else None,
        idempotency_keys=tuple(idempotency_keys),
        lineage_summary=lineage_summary,
        warnings=tuple(dict.fromkeys(warnings)),
    )


def read_breadth_observations_handoff_jsonl(path: str | Path) -> tuple[dict[str, Any], ...]:
    path = Path(path)
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if isinstance(payload, dict):
                records.append(payload)
    return tuple(records)
