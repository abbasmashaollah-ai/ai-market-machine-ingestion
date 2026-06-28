"""Warehouse-shaped payload builders for sector money flow observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from hashlib import sha256
from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class SectorMoneyFlowBuildMetadata:
    source_vendor: str = "unknown_vendor"
    source_dataset: str = "sector_money_flow"
    source_file_name: str | None = None
    source_file_path: str | None = None
    source_uri: str | None = None
    source_sha256: str = ""
    schema_version: str = "sector_money_flow_jsonl_v1"
    lineage: dict[str, object] = field(default_factory=dict)
    evidence: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)


def _normalize_text(value: object | None) -> str:
    return str(value).strip() if value is not None else ""


def _normalize_symbol(symbol: object) -> str:
    normalized = _normalize_text(symbol).upper()
    if not normalized:
        raise ValueError("sector_symbol is required")
    return normalized


def _normalize_date_value(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _metadata_to_dict(metadata: SectorMoneyFlowBuildMetadata | Mapping[str, object] | None) -> dict[str, object]:
    if metadata is None:
        metadata = SectorMoneyFlowBuildMetadata()
    if isinstance(metadata, SectorMoneyFlowBuildMetadata):
        return {
            "source_vendor": metadata.source_vendor,
            "source_dataset": metadata.source_dataset,
            "source_file_name": metadata.source_file_name,
            "source_file_path": metadata.source_file_path,
            "source_uri": metadata.source_uri,
            "source_sha256": metadata.source_sha256,
            "schema_version": metadata.schema_version,
            "lineage": dict(metadata.lineage),
            "evidence": dict(metadata.evidence),
            "metadata": dict(metadata.metadata),
        }
    result = dict(metadata)
    result.setdefault("source_vendor", "unknown_vendor")
    result.setdefault("source_dataset", "sector_money_flow")
    result.setdefault("source_sha256", "")
    result.setdefault("schema_version", "sector_money_flow_jsonl_v1")
    result.setdefault("lineage", {})
    result.setdefault("evidence", {})
    result.setdefault("metadata", {})
    return result


def _deterministic_idempotency_key(source_vendor: str, source_dataset: str, source_sha256: str, observation_date: str, sector_symbol: str, schema_version: str) -> str:
    payload = "|".join([source_vendor, source_dataset, source_sha256, observation_date, sector_symbol, schema_version])
    return sha256(payload.encode("utf-8")).hexdigest()


def build_sector_money_flow_observation(
    row: Mapping[str, object],
    metadata: SectorMoneyFlowBuildMetadata | Mapping[str, object] | None = None,
) -> dict[str, object]:
    metadata_dict = _metadata_to_dict(metadata)
    observation_date = _normalize_date_value(row.get("observation_date"))
    if not observation_date:
        raise ValueError("observation_date is required")
    sector_symbol = _normalize_symbol(row.get("sector_symbol"))
    source_vendor = _normalize_text(row.get("source_vendor") or metadata_dict["source_vendor"])
    source_dataset = _normalize_text(row.get("source_dataset") or metadata_dict["source_dataset"])
    source_sha256 = _normalize_text(row.get("source_sha256") or metadata_dict["source_sha256"])
    schema_version = _normalize_text(row.get("schema_version") or metadata_dict["schema_version"])
    idempotency_key = _normalize_text(row.get("idempotency_key")) or _deterministic_idempotency_key(
        source_vendor, source_dataset, source_sha256, observation_date, sector_symbol, schema_version
    )
    generated_at = _normalize_date_value(row.get("generated_at"))
    if not generated_at:
        raise ValueError("generated_at is required")

    payload = {
        "observation_date": observation_date,
        "sector_symbol": sector_symbol,
        "sector_name": row.get("sector_name"),
        "universe_key": row.get("universe_key"),
        "source_vendor": source_vendor,
        "source_dataset": source_dataset,
        "source_sha256": source_sha256,
        "source_file_name": row.get("source_file_name") or metadata_dict.get("source_file_name"),
        "source_file_path": row.get("source_file_path") or metadata_dict.get("source_file_path"),
        "source_uri": row.get("source_uri") or metadata_dict.get("source_uri"),
        "generated_at": generated_at,
        "schema_version": schema_version,
        "idempotency_key": idempotency_key,
        "metadata": dict(row.get("metadata") or metadata_dict.get("metadata") or {}),
        "evidence": dict(row.get("evidence") or metadata_dict.get("evidence") or {}),
        "lineage": dict(row.get("lineage") or metadata_dict.get("lineage") or {}),
        "sector_etf_volume_confirmed_move": row.get("sector_etf_volume_confirmed_move"),
        "sector_etf_dollar_volume": row.get("sector_etf_dollar_volume"),
        "accumulation_distribution_proxy": row.get("accumulation_distribution_proxy"),
        "inflow_outflow_proxy": row.get("inflow_outflow_proxy"),
        "flow_confidence": row.get("flow_confidence"),
        "flow_support_score": row.get("flow_support_score"),
    }
    return payload


def build_sector_money_flow_observations(
    rows: Sequence[Mapping[str, object]],
    metadata: SectorMoneyFlowBuildMetadata | Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    return [build_sector_money_flow_observation(row, metadata=metadata) for row in rows]
