from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import hashlib
from typing import Any

try:
    from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError
except Exception:  # pragma: no cover - keep import safe when botocore is unavailable.
    class _MissingBotocoreError(Exception):
        pass

    BotoCoreError = _MissingBotocoreError  # type: ignore[assignment]
    ClientError = _MissingBotocoreError  # type: ignore[assignment]
    EndpointConnectionError = _MissingBotocoreError  # type: ignore[assignment]

from .options_flat_file_manifest import OPTIONS_PREFIX, OPTIONS_SAMPLE_KEY, classify_config, redacted_key_tail

APPROVAL_PHRASE = "APPROVE OPTIONS FLAT FILE SINGLE DATE LOCAL QUARANTINE DOWNLOAD"
DEFAULT_DATE = "2025-11-05"
DEFAULT_LOCAL_RELATIVE_PATH = Path("outputs/quarantine/options_flat_files/massive_options_day_aggs_2025-11-05.csv.gz")


@dataclass(frozen=True, slots=True)
class OptionsQuarantineSafeResult:
    approval_required: bool
    approval_phrase_matched: bool
    vendor_call_attempted: bool
    remote_head_object_attempted: bool
    download_attempted: bool
    download_succeeded: bool
    decompression_attempted: bool
    parse_attempted: bool
    export_attempted: bool
    db_read_attempted: bool
    db_write_attempted: bool
    ingestion_attempted: bool
    scheduler_activation_attempted: bool
    production_mutation_attempted: bool
    blockers: tuple[str, ...]
    next_allowed_step: str


def options_output_path(date_value: str = DEFAULT_DATE, quarantine_dir: str | Path = "outputs/quarantine/options_flat_files") -> Path:
    return Path(quarantine_dir) / f"massive_options_day_aggs_{date_value}.csv.gz"


def options_object_key(date_value: str | date = DEFAULT_DATE) -> str:
    if isinstance(date_value, date):
        day = date_value
    else:
        day = datetime.strptime(str(date_value), "%Y-%m-%d").date()
    return f"{OPTIONS_PREFIX}/{day:%Y/%m}/{day:%Y-%m-%d}.csv.gz"


def redacted_options_tail(date_value: str | date = DEFAULT_DATE) -> str:
    return redacted_key_tail(options_object_key(date_value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_client_error(error: Exception) -> tuple[str, str]:
    error_name = error.__class__.__name__
    if error_name == "EndpointConnectionError" or isinstance(error, EndpointConnectionError):
        return "endpoint_connection_error", "remote check failed safely"
    response = getattr(error, "response", {}) if hasattr(error, "response") else {}
    error_data = response.get("Error", {}) if isinstance(response, dict) else {}
    raw_code = str(error_data.get("Code") or "client_error")
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode") if isinstance(response, dict) else None
    if str(status) == "403":
        return "forbidden", "remote check failed safely"
    if raw_code == "AccessDenied":
        return "access_denied", "remote check failed safely"
    if raw_code == "NoSuchBucket":
        return "bucket_not_found", "remote check failed safely"
    if raw_code == "NoSuchKey":
        return "missing_object", "remote check failed safely"
    return "client_error", "remote check failed safely"


def _safe_write_stream(response: dict[str, Any], path: Path) -> None:
    body = response.get("Body") if isinstance(response, dict) else None
    with path.open("wb") as handle:
        if body is not None and hasattr(body, "read"):
            while True:
                chunk = body.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)


def download_single_date_quarantine(
    *,
    env: dict[str, str],
    enabled: bool,
    approval_phrase: str,
    date_value: str = DEFAULT_DATE,
    quarantine_dir: str | Path = "outputs/quarantine/options_flat_files",
    overwrite_local_file: bool = False,
    boto3_module: Any | None = None,
) -> dict[str, object]:
    output_path = options_output_path(date_value, quarantine_dir)
    output_parent = output_path.parent
    blockers = [
        "production handoff generation is not authorized",
        "no decompression, parsing, export, DB reads, DB writes, ingestion, scheduler activation, or production mutation are permitted",
    ]
    approval_phrase_matched = approval_phrase == APPROVAL_PHRASE
    approval_required = True
    vendor_call_attempted = False
    remote_head_object_attempted = False
    remote_download_error_code_redacted = ""
    remote_download_error_message_redacted = ""
    download_attempted = False
    download_succeeded = False
    local_file_exists = output_path.exists()
    local_file_size_bytes = output_path.stat().st_size if output_path.exists() else 0
    local_file_sha256 = sha256_file(output_path) if output_path.exists() else ""
    config_classification = classify_config(env)

    if not enabled:
        blockers.append("download is disabled by default")
    if not approval_phrase_matched:
        blockers.append("approval phrase does not match")
    if config_classification != "polygon_flat_file":
        blockers.append("Polygon flat-file configuration is incomplete or ambiguous")
    if output_path.exists() and not overwrite_local_file:
        blockers.append("local file already exists and overwrite is not approved")

    if not enabled or not approval_phrase_matched or config_classification != "polygon_flat_file":
        return {
            "approval_required": approval_required,
            "approval_phrase_matched": approval_phrase_matched,
            "config_classification": config_classification,
            "vendor_call_attempted": False,
            "remote_head_object_attempted": False,
            "download_attempted": False,
            "download_succeeded": False,
            "decompression_attempted": False,
            "parse_attempted": False,
            "export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "redacted_key_tail": redacted_options_tail(date_value),
            "output_path": str(output_path),
            "output_file_exists": local_file_exists,
            "output_file_size_bytes": local_file_size_bytes,
            "output_sha256": local_file_sha256,
            "remote_download_error_code_redacted": remote_download_error_code_redacted,
            "remote_download_error_message_redacted": remote_download_error_message_redacted,
            "blockers": blockers,
            "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
        }

    try:
        if boto3_module is None:
            import boto3 as boto3_module  # type: ignore[no-redef]
        client = boto3_module.client(
            "s3",
            aws_access_key_id=env.get("POLYGON_FLAT_FILE_ACCESS_KEY_ID"),
            aws_secret_access_key=env.get("POLYGON_FLAT_FILE_SECRET_ACCESS_KEY"),
            endpoint_url=env.get("POLYGON_FLAT_FILE_ENDPOINT"),
        )
        vendor_call_attempted = True
        key = options_object_key(date_value)
        bucket = env.get("POLYGON_FLAT_FILE_BUCKET")
        remote_head_object_attempted = True
        response = client.head_object(Bucket=bucket, Key=key)
        content_length_present = bool(isinstance(response, dict) and response.get("ContentLength") is not None)
        download_attempted = True
        if output_path.exists() and not overwrite_local_file:
            blockers.append("local file already exists and overwrite is not approved")
            return {
                "approval_required": approval_required,
                "approval_phrase_matched": approval_phrase_matched,
                "config_classification": config_classification,
                "vendor_call_attempted": vendor_call_attempted,
                "remote_head_object_attempted": remote_head_object_attempted,
                "download_attempted": download_attempted,
                "download_succeeded": False,
                "decompression_attempted": False,
                "parse_attempted": False,
                "export_attempted": False,
                "db_read_attempted": False,
                "db_write_attempted": False,
                "ingestion_attempted": False,
                "scheduler_activation_attempted": False,
                "production_mutation_attempted": False,
                "redacted_key_tail": redacted_options_tail(date_value),
                "output_path": str(output_path),
                "output_file_exists": True,
                "output_file_size_bytes": output_path.stat().st_size,
                "output_sha256": sha256_file(output_path),
                "content_length_present": content_length_present,
                "remote_download_error_code_redacted": remote_download_error_code_redacted,
                "remote_download_error_message_redacted": remote_download_error_message_redacted,
                "blockers": blockers,
                "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
            }
        output_parent.mkdir(parents=True, exist_ok=True)
        response = client.get_object(Bucket=bucket, Key=key)
        _safe_write_stream(response, output_path)
        download_succeeded = output_path.exists()
        local_file_exists = download_succeeded
        local_file_size_bytes = output_path.stat().st_size if output_path.exists() else 0
        local_file_sha256 = sha256_file(output_path) if output_path.exists() else ""
        return {
            "approval_required": approval_required,
            "approval_phrase_matched": approval_phrase_matched,
            "config_classification": config_classification,
            "vendor_call_attempted": vendor_call_attempted,
            "remote_head_object_attempted": remote_head_object_attempted,
            "download_attempted": download_attempted,
            "download_succeeded": download_succeeded,
            "decompression_attempted": False,
            "parse_attempted": False,
            "export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "redacted_key_tail": redacted_options_tail(date_value),
            "output_path": str(output_path),
            "output_file_exists": local_file_exists,
            "output_file_size_bytes": local_file_size_bytes,
            "output_sha256": local_file_sha256,
            "content_length_present": content_length_present,
            "remote_download_error_code_redacted": remote_download_error_code_redacted,
            "remote_download_error_message_redacted": remote_download_error_message_redacted,
            "blockers": blockers,
            "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
        }
    except Exception as exc:
        if str(exc) == "dependency_missing":
            blockers.append("remote download blocked safely: dependency_missing")
            remote_download_error_code_redacted = "dependency_missing"
            remote_download_error_message_redacted = "remote download requires boto3"
            vendor_call_attempted = False
            remote_head_object_attempted = False
        else:
            code, message = _safe_client_error(exc)
            blockers.append(f"download blocked safely: {code}")
            remote_download_error_code_redacted = code
            remote_download_error_message_redacted = message
        return {
            "approval_required": approval_required,
            "approval_phrase_matched": approval_phrase_matched,
            "config_classification": config_classification,
            "vendor_call_attempted": vendor_call_attempted,
            "remote_head_object_attempted": remote_head_object_attempted,
            "download_attempted": download_attempted,
            "download_succeeded": False,
            "decompression_attempted": False,
            "parse_attempted": False,
            "export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "redacted_key_tail": redacted_options_tail(date_value),
            "output_path": str(output_path),
            "output_file_exists": False,
            "output_file_size_bytes": 0,
            "output_sha256": "",
            "remote_download_error_code_redacted": remote_download_error_code_redacted,
            "remote_download_error_message_redacted": remote_download_error_message_redacted,
            "blockers": blockers,
            "next_allowed_step": "explicit approved single-date local quarantine download only, not export",
        }
