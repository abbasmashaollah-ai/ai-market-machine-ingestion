from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

SUPPORTED_OPTIONS_HANDBACK_DOMAINS = (
    "options_day_aggregates",
    "options_contracts_master",
    "options_open_interest",
    "options_greeks_iv",
)

_DOMAIN_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "options_day_aggregates": (
        "contract_symbol",
        "underlying_symbol",
        "expiration_date",
        "strike_price",
        "option_type",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "transactions",
    ),
    "options_contracts_master": (
        "contract_symbol",
        "underlying_symbol",
        "expiration_date",
        "strike_price",
        "option_type",
    ),
    "options_open_interest": (
        "contract_symbol",
        "underlying_symbol",
        "expiration_date",
        "strike_price",
        "option_type",
        "observation_date",
        "open_interest",
    ),
    "options_greeks_iv": (
        "contract_symbol",
        "underlying_symbol",
        "expiration_date",
        "strike_price",
        "option_type",
        "observation_timestamp",
        "implied_volatility",
    ),
}


@dataclass(frozen=True, slots=True)
class OptionsHandoffWriteResult:
    attempted_count: int
    written_count: int
    rejected_count: int
    output_path: str
    producer_run_id: str
    source_dataset: str
    vendor: str
    errors: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]


def _is_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return False
    return True


def _normalize_metadata(value: Any) -> Any:
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return value
    if isinstance(value, Sequence):
        return list(value)
    return value


def _safe_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("optional metadata must be a string when provided")
    return value


def _validate_record(record: Mapping[str, Any]) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    domain = record.get("source_dataset")
    if not isinstance(domain, str) or not domain:
        errors.append("missing domain")
        return None, errors
    if domain not in SUPPORTED_OPTIONS_HANDBACK_DOMAINS:
        errors.append(f"unsupported domain: {domain}")
        return domain, errors
    for field_name in _DOMAIN_REQUIRED_FIELDS[domain]:
        if field_name not in record:
            errors.append(f"missing required field: {field_name}")
    return domain, errors


def write_options_handoff_jsonl(
    records: Sequence[Mapping[str, Any]],
    output_path: str | Path,
    producer_run_id: str,
    source_dataset: str,
    vendor: str,
    source_file_name: str | None = None,
    source_file_path: str | None = None,
    source_sha256: str | None = None,
    lineage: Sequence[str] | None = None,
    warnings: Sequence[str] | None = None,
) -> dict[str, Any]:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stamped_lineage = _normalize_metadata(lineage)
    stamped_warnings = _normalize_metadata(warnings)
    errors: list[dict[str, Any]] = []
    written_records: list[dict[str, Any]] = []

    for index, record in enumerate(records):
        attempted_record = deepcopy(dict(record))
        _, validation_errors = _validate_record(attempted_record)
        if not _is_json_serializable(attempted_record):
            validation_errors.append("record contains non-json-serializable values")
        if validation_errors:
            errors.append({"index": index, "errors": validation_errors})
            continue

        stamped = dict(attempted_record)
        stamped.setdefault("source_dataset", source_dataset)
        stamped.setdefault("vendor", vendor)
        stamped.setdefault("producer_run_id", producer_run_id)
        stamped.setdefault("lineage", stamped_lineage)
        stamped.setdefault("warnings", stamped_warnings)
        if source_file_name is not None:
            stamped.setdefault("source_file_name", _safe_optional_text(source_file_name))
        if source_file_path is not None:
            stamped.setdefault("source_file_path", _safe_optional_text(source_file_path))
        if source_sha256 is not None:
            stamped.setdefault("source_sha256", _safe_optional_text(source_sha256))
        written_records.append(stamped)

    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in written_records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    return {
        "attempted_count": len(records),
        "written_count": len(written_records),
        "rejected_count": len(errors),
        "output_path": str(output_path),
        "producer_run_id": producer_run_id,
        "source_dataset": source_dataset,
        "vendor": vendor,
        "errors": tuple(errors),
        "warnings": tuple(stamped_warnings),
    }


def read_options_handoff_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                record = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSONL at line {line_number}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Malformed JSONL at line {line_number}: expected JSON object")
            records.append(record)
    return records
