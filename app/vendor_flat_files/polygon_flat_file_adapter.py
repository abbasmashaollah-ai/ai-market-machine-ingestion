from __future__ import annotations

from datetime import date, datetime, timedelta
import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError
except Exception:  # pragma: no cover - botocore is installed in normal runs, but keep import-safe.
    class _MissingBotocoreError(Exception):
        pass

    BotoCoreError = _MissingBotocoreError  # type: ignore[assignment]
    ClientError = _MissingBotocoreError  # type: ignore[assignment]
    EndpointConnectionError = _MissingBotocoreError  # type: ignore[assignment]

SECTOR_ETF_UNIVERSE: tuple[str, ...] = (
    "SPY",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
)
SECTOR_SYMBOLS: tuple[str, ...] = SECTOR_ETF_UNIVERSE[1:]

REQUIRED_CONFIG_NAMES: tuple[str, ...] = (
    "POLYGON_API_KEY",
    "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
    "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
    "POLYGON_FLAT_FILE_ENDPOINT",
    "POLYGON_FLAT_FILE_BUCKET",
    "POLYGON_FLAT_FILE_PREFIX",
)

EXPECTED_FLAT_FILE_DATASET_TYPE = "daily_ohlcv"
BENCHMARK_SYMBOL = "SPY"


@dataclass(frozen=True, slots=True)
class PolygonFlatFileAdapterSummary:
    polygon_flat_file_source_selected: bool
    flat_file_adapter_detected: bool
    local_parser_detected: bool
    handoff_builder_detected: bool
    sector_etf_universe_detected: bool
    production_eligible_generation_authorized: bool
    synthetic_forbidden: bool
    fixture_only_forbidden: bool
    required_config_names: tuple[str, ...]
    missing_config_names: tuple[str, ...]
    required_sector_symbols: tuple[str, ...]
    benchmark_symbol: str
    expected_flat_file_dataset_type: str
    credentials_printed: bool
    blockers: tuple[str, ...]
    next_allowed_step: str


def required_config_names() -> tuple[str, ...]:
    return REQUIRED_CONFIG_NAMES


def sector_etf_symbols() -> tuple[str, ...]:
    return SECTOR_SYMBOLS


def sector_etf_universe_symbols() -> tuple[str, ...]:
    return SECTOR_ETF_UNIVERSE


def benchmark_symbol() -> str:
    return BENCHMARK_SYMBOL


def expected_flat_file_dataset_type() -> str:
    return EXPECTED_FLAT_FILE_DATASET_TYPE


def detect_config_presence(env: dict[str, str]) -> dict[str, list[str] | bool]:
    present = [name for name in REQUIRED_CONFIG_NAMES if env.get(name)]
    missing = [name for name in REQUIRED_CONFIG_NAMES if not env.get(name)]
    return {
        "credentials_present": bool(present),
        "present_config_names": present,
        "missing_config_names": missing,
    }


def summarize_capability(*, env: dict[str, str], local_parser_detected: bool, handoff_builder_detected: bool) -> PolygonFlatFileAdapterSummary:
    presence = detect_config_presence(env)
    flat_file_adapter_detected = any(
        env.get(name)
        for name in (
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
            "POLYGON_FLAT_FILE_ENDPOINT",
            "POLYGON_FLAT_FILE_BUCKET",
            "POLYGON_FLAT_FILE_PREFIX",
        )
    )
    blockers = [
        "production handoff generation is not authorized",
        "no remote bucket listing or downloads are permitted in this adapter scaffold",
    ]
    if not flat_file_adapter_detected:
        blockers.append("flat-file adapter configuration is not fully present")
    if not local_parser_detected:
        blockers.append("local parser scaffold not detected")
    if not handoff_builder_detected:
        blockers.append("handoff builder scaffold not detected")
    return PolygonFlatFileAdapterSummary(
        polygon_flat_file_source_selected=True,
        flat_file_adapter_detected=flat_file_adapter_detected,
        local_parser_detected=local_parser_detected,
        handoff_builder_detected=handoff_builder_detected,
        sector_etf_universe_detected=True,
        production_eligible_generation_authorized=False,
        synthetic_forbidden=True,
        fixture_only_forbidden=True,
        required_config_names=REQUIRED_CONFIG_NAMES,
        missing_config_names=tuple(presence["missing_config_names"]),
        required_sector_symbols=SECTOR_SYMBOLS,
        benchmark_symbol=BENCHMARK_SYMBOL,
        expected_flat_file_dataset_type=EXPECTED_FLAT_FILE_DATASET_TYPE,
        credentials_printed=False,
        blockers=tuple(blockers),
        next_allowed_step="read-only approved-vendor flat-file sample inspection or explicit production approval workflow, not export",
    )


class PolygonFlatFileAdapter:
    def __init__(self, env: dict[str, str] | None = None) -> None:
        self._env = dict(env or {})

    def safe_summary(self) -> dict[str, object]:
        summary = summarize_capability(
            env=self._env,
            local_parser_detected=Path("app/vendor_flat_files/local_ohlcv_parser.py").exists(),
            handoff_builder_detected=Path("app/vendor_flat_files/ohlcv_handoff_builder.py").exists(),
        )
        return {
            "polygon_flat_file_source_selected": summary.polygon_flat_file_source_selected,
            "flat_file_adapter_detected": summary.flat_file_adapter_detected,
            "local_parser_detected": summary.local_parser_detected,
            "handoff_builder_detected": summary.handoff_builder_detected,
            "sector_etf_universe_detected": summary.sector_etf_universe_detected,
            "production_eligible_generation_authorized": summary.production_eligible_generation_authorized,
            "synthetic_forbidden": summary.synthetic_forbidden,
            "fixture_only_forbidden": summary.fixture_only_forbidden,
            "required_config_names": list(summary.required_config_names),
            "missing_config_names": list(summary.missing_config_names),
            "required_sector_symbols": list(summary.required_sector_symbols),
            "sector_etf_universe_symbols": list(SECTOR_ETF_UNIVERSE),
            "benchmark_symbol": summary.benchmark_symbol,
            "expected_flat_file_dataset_type": summary.expected_flat_file_dataset_type,
            "credentials_printed": summary.credentials_printed,
            "blockers": list(summary.blockers),
            "next_allowed_step": summary.next_allowed_step,
            "credentials_present": bool(detect_config_presence(self._env)["credentials_present"]),
        }

    def list_remote_flat_files(self) -> list[str]:
        raise NotImplementedError("remote listing is disabled in the adapter scaffold")

    def download_flat_file(self, *_: Any, **__: Any) -> None:
        raise NotImplementedError("download is disabled in the adapter scaffold")

    def build_manifest(self, *_: Any, **__: Any) -> dict[str, Any]:
        raise NotImplementedError("manifest construction is disabled in the adapter scaffold")

    def build_production_handoff(self, *_: Any, **__: Any) -> dict[str, Any]:
        raise NotImplementedError("production handoff generation is unauthorized")

    @staticmethod
    def boto3_available() -> bool:
        return importlib.util.find_spec("boto3") is not None

    def build_remote_listing_client(self) -> Any:
        if not self.boto3_available():
            raise RuntimeError("boto3 is required for remote listing preflight")
        import boto3

        return boto3.client(
            "s3",
            aws_access_key_id=self._env.get("POLYGON_FLAT_FILE_ACCESS_KEY_ID"),
            aws_secret_access_key=self._env.get("POLYGON_FLAT_FILE_SECRET_ACCESS_KEY"),
            endpoint_url=self._env.get("POLYGON_FLAT_FILE_ENDPOINT"),
        )

    def list_remote_objects(self, *, max_keys: int) -> list[dict[str, str]]:
        client = self.build_remote_listing_client()
        response = client.list_objects_v2(
            Bucket=self._env.get("POLYGON_FLAT_FILE_BUCKET"),
            Prefix=self._env.get("POLYGON_FLAT_FILE_PREFIX"),
            MaxKeys=max_keys,
        )
        contents = response.get("Contents", []) if isinstance(response, dict) else []
        return [obj for obj in contents if isinstance(obj, dict) and "Key" in obj]

    @staticmethod
    def _normalize_date(value: str | date) -> date:
        if isinstance(value, date):
            return value
        return datetime.strptime(value, "%Y-%m-%d").date()

    @staticmethod
    def _date_range(start_date: str | date, end_date: str | date, max_days: int) -> list[date]:
        start = PolygonFlatFileAdapter._normalize_date(start_date)
        end = PolygonFlatFileAdapter._normalize_date(end_date)
        if end < start:
            start, end = end, start
        days: list[date] = []
        current = start
        while current <= end and len(days) < max_days:
            days.append(current)
            current += timedelta(days=1)
        return days

    @staticmethod
    def redacted_csv_gzip_tail(value: str | date) -> str:
        if isinstance(value, str):
            match = re.search(r"(?P<tail>\d{4}/\d{2}/\d{4}-\d{2}-\d{2}\.csv\.gz)$", value)
            if match:
                return match.group("tail")
            legacy_match = re.search(r"(?P<tail>\d{2}/\d{4}-\d{2}-\d{2}\.csv\.gz)$", value)
            if legacy_match:
                return legacy_match.group("tail")
        day = PolygonFlatFileAdapter._normalize_date(value)
        return f"{day:%Y/%m/%Y-%m-%d.csv.gz}"

    @staticmethod
    def _basename_matches_requested_date(name: str, day: date) -> bool:
        return name == f"{day:%Y-%m-%d}.csv.gz"

    @staticmethod
    def _tail_matches_requested_date(tail: str, day: date) -> bool:
        canonical_tail = f"{day:%Y/%m/%Y-%m-%d.csv.gz}"
        basename = f"{day:%Y-%m-%d}.csv.gz"
        tail_basename = tail.rsplit("/", 1)[-1]
        return tail == canonical_tail or tail_basename == basename

    @staticmethod
    def stock_day_aggs_object_key(value: str | date) -> str:
        day = PolygonFlatFileAdapter._normalize_date(value)
        return f"us_stocks_sip/day_aggs_v1/{day:%Y/%m}/{day:%Y-%m-%d}.csv.gz"

    @staticmethod
    def sha256_prefix(value: str | bytes, *, prefix_len: int = 12) -> str:
        import hashlib

        payload = value if isinstance(value, bytes) else value.encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:prefix_len]

    @staticmethod
    def _month_listing_max_keys(requested: int) -> int:
        return min(max(requested, 100), 250)

    def list_remote_manifest_objects(self, *, start_date: str | date, end_date: str | date, max_days: int) -> list[dict[str, str]]:
        client = self.build_remote_listing_client()
        dates = self._date_range(start_date, end_date, max_days)
        results: list[dict[str, str]] = []
        months: dict[tuple[int, int], list[date]] = {}
        for day in dates:
            months.setdefault((day.year, day.month), []).append(day)
        for (year, month), month_dates in months.items():
            lookup_prefix = f"us_stocks_sip/day_aggs_v1/{year:04d}/{month:02d}/"
            response = client.list_objects_v2(
                Bucket=self._env.get("POLYGON_FLAT_FILE_BUCKET"),
                Prefix=lookup_prefix,
                MaxKeys=self._month_listing_max_keys(max_days),
            )
            contents = response.get("Contents", []) if isinstance(response, dict) else []
            observed_by_tail: dict[str, dict[str, str]] = {}
            csv_gz_count = 0
            for obj in contents:
                if not isinstance(obj, dict):
                    continue
                key_value = str(obj.get("Key") or "")
                if not key_value.endswith(".csv.gz"):
                    continue
                csv_gz_count += 1
                basename_tail = key_value.rsplit("/", 1)[-1]
                safe_tail = "/".join(key_value.split("/")[-3:]) if key_value.count("/") >= 2 else basename_tail
                tail = self.redacted_csv_gzip_tail(key_value) if "/" in key_value else ""
                if tail and tail not in observed_by_tail:
                    observed_by_tail[tail] = obj
                if basename_tail and basename_tail not in observed_by_tail:
                    observed_by_tail[basename_tail] = obj
                if safe_tail and safe_tail not in observed_by_tail:
                    observed_by_tail[safe_tail] = obj
            for day in month_dates:
                expected_tail = f"{day:%Y/%m/%Y-%m-%d.csv.gz}"
                expected_filename = f"{day:%Y-%m-%d}.csv.gz"
                key_tail = expected_tail
                basename_tail = expected_filename
                match = observed_by_tail.get(key_tail)
                if not isinstance(match, dict):
                    match = observed_by_tail.get(basename_tail)
                if not isinstance(match, dict):
                    match = observed_by_tail.get(expected_tail)
                if isinstance(match, dict):
                    result = {
                        "date": day.isoformat(),
                        "redacted_key_tail": expected_tail,
                        "object_present": True,
                        "expected_filename": expected_filename,
                        "expected_tail": expected_tail,
                        "remote_list_csv_gz_object_count_seen": csv_gz_count,
                        "remote_list_basename_match": basename_tail in observed_by_tail,
                        "remote_list_suffix_match": expected_tail in observed_by_tail or key_tail in observed_by_tail,
                        "Size": match.get("Size"),
                        "LastModified": match.get("LastModified"),
                        "ETag": match.get("ETag"),
                    }
                    results.append(result)
                else:
                    results.append(
                        {
                            "date": day.isoformat(),
                            "redacted_key_tail": expected_tail,
                            "object_present": False,
                            "expected_filename": expected_filename,
                            "expected_tail": expected_tail,
                            "remote_list_csv_gz_object_count_seen": csv_gz_count,
                            "remote_list_basename_match": basename_tail in observed_by_tail,
                            "remote_list_suffix_match": expected_tail in observed_by_tail,
                        }
                    )
        return results

    def resolve_remote_manifest_object_for_date(self, value: str | date) -> dict[str, Any] | None:
        day = PolygonFlatFileAdapter._normalize_date(value)
        client = self.build_remote_listing_client()
        lookup_prefix = f"us_stocks_sip/day_aggs_v1/{day:%Y/%m}/"
        response = client.list_objects_v2(
            Bucket=self._env.get("POLYGON_FLAT_FILE_BUCKET"),
            Prefix=lookup_prefix,
            MaxKeys=self._month_listing_max_keys(100),
        )
        contents = response.get("Contents", []) if isinstance(response, dict) else []
        expected_tail = f"{day:%Y/%m/%Y-%m-%d.csv.gz}"
        expected_filename = f"{day:%Y-%m-%d}.csv.gz"
        for obj in contents:
            if not isinstance(obj, dict):
                continue
            key_value = str(obj.get("Key") or "")
            if not key_value.endswith(".csv.gz"):
                continue
            basename_tail = key_value.rsplit("/", 1)[-1]
            safe_tail = "/".join(key_value.split("/")[-3:]) if key_value.count("/") >= 2 else basename_tail
            if basename_tail == expected_filename or key_value.endswith(expected_tail) or safe_tail == expected_tail:
                result = {
                    "date": day.isoformat(),
                    "redacted_key_tail": expected_tail,
                    "object_present": True,
                    "expected_filename": expected_filename,
                    "expected_tail": expected_tail,
                    "remote_list_basename_match": basename_tail == expected_filename,
                    "remote_list_suffix_match": key_value.endswith(expected_tail) or safe_tail == expected_tail,
                    "_resolved_key_internal": key_value,
                    "Size": obj.get("Size"),
                    "LastModified": obj.get("LastModified"),
                    "ETag": obj.get("ETag"),
                }
                return result
        return None

    def download_single_date_object(self, *, value: str | date, local_path: str | Path, overwrite: bool = False) -> dict[str, Any]:
        path = Path(local_path)
        day = self._normalize_date(value)
        requested_tail = self.redacted_csv_gzip_tail(day)
        if path.exists() and not overwrite:
            return {
                "downloaded": False,
                "skipped_existing": True,
                "local_file_exists": True,
                "local_file_size_bytes": path.stat().st_size,
                "local_file_sha256": _sha256_file(path),
                "redacted_key_tail": requested_tail,
                "resolved_key_present": False,
                "resolved_key_tail_matches_requested_date": False,
                "resolved_key_sha256_prefix": "",
                "listed_key_sha256_prefix": "",
                "resolved_key_matches_listed_key": False,
                "content_length_present": False,
                "local_quarantine_path": str(path),
            }
        path.parent.mkdir(parents=True, exist_ok=True)
        if not self.boto3_available():
            raise RuntimeError("boto3 is required for remote download preflight")
        resolved = self.resolve_remote_manifest_object_for_date(value)
        resolved_key_value = str(resolved.get("_resolved_key_internal") or resolved.get("Key") or "") if resolved else ""
        if not resolved or not resolved.get("object_present") or not resolved_key_value:
            return {
                "downloaded": False,
                "skipped_existing": False,
                "local_file_exists": False,
                "local_file_size_bytes": 0,
                "local_file_sha256": "",
                "redacted_key_tail": requested_tail,
                "resolved_key_present": False,
                "resolved_key_tail_matches_requested_date": False,
                "resolved_key_sha256_prefix": "",
                "listed_key_sha256_prefix": "",
                "resolved_key_matches_listed_key": False,
                "content_length_present": False,
                "local_quarantine_path": str(path),
        }
        listed_key = resolved_key_value
        resolved_key = listed_key
        key_tail = requested_tail
        key_hash = self.sha256_prefix(resolved_key)
        tail_matches = self._tail_matches_requested_date(key_tail, day)
        client = self.build_remote_listing_client()
        try:
            response = client.get_object(Bucket=self._env.get("POLYGON_FLAT_FILE_BUCKET"), Key=resolved_key)
            body = response.get("Body") if isinstance(response, dict) else None
            content_length_present = bool(isinstance(response, dict) and response.get("ContentLength") is not None)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as handle:
                if body is not None and hasattr(body, "read"):
                    while True:
                        chunk = body.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
        except Exception as error:
            code, redacted_code, message = self.classify_remote_listing_error(error)
            return {
                "downloaded": False,
                "skipped_existing": False,
                "local_file_exists": False,
                "local_file_size_bytes": 0,
                "local_file_sha256": "",
                "redacted_key_tail": key_tail,
                "resolved_key_present": True,
                "resolved_key_tail_matches_requested_date": tail_matches,
                "resolved_key_sha256_prefix": key_hash,
                "listed_key_sha256_prefix": self.sha256_prefix(listed_key),
                "resolved_key_matches_listed_key": resolved_key == listed_key,
                "content_length_present": False,
                "local_quarantine_path": str(path),
                "remote_download_status": code,
                "remote_download_error_code_redacted": redacted_code,
                "remote_download_error_message_redacted": message,
            }
        return {
            "downloaded": True,
            "skipped_existing": False,
            "local_file_exists": path.exists(),
            "local_file_size_bytes": path.stat().st_size if path.exists() else 0,
            "local_file_sha256": _sha256_file(path) if path.exists() else "",
            "redacted_key_tail": key_tail,
            "resolved_key_present": True,
            "resolved_key_tail_matches_requested_date": tail_matches,
            "resolved_key_sha256_prefix": key_hash,
            "listed_key_sha256_prefix": self.sha256_prefix(listed_key),
            "resolved_key_matches_listed_key": resolved_key == listed_key,
            "content_length_present": content_length_present,
            "local_quarantine_path": str(path),
        }

    @staticmethod
    def classify_remote_listing_error(error: Exception) -> tuple[str, str, str]:
        code = "client_error"
        message = "remote listing failed safely"
        redacted_code = "client_error"
        error_name = error.__class__.__name__
        if isinstance(error, EndpointConnectionError) or error_name == "EndpointConnectionError":
            code = "endpoint_connection_error"
            redacted_code = code
            message = "endpoint connection error"
            return code, redacted_code, message
        response = getattr(error, "response", {}) if hasattr(error, "response") else {}
        error_data = response.get("Error", {}) if isinstance(response, dict) else {}
        raw_code = str(error_data.get("Code") or "client_error")
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode") if isinstance(response, dict) else None
        if isinstance(error, ClientError) or error_name == "ClientError" or isinstance(response, dict):
            if str(status) == "403":
                code = "forbidden"
            elif raw_code == "AccessDenied":
                code = "access_denied"
            elif raw_code == "InvalidAccessKeyId":
                code = "invalid_access_key"
            elif raw_code == "SignatureDoesNotMatch":
                code = "signature_mismatch"
            elif raw_code == "NoSuchBucket":
                code = "bucket_not_found"
            else:
                code = "client_error"
            redacted_code = code
            message = "remote listing failed safely"
            return code, redacted_code, message
        if isinstance(error, BotoCoreError) or error_name == "BotoCoreError":
            code = "client_error"
            redacted_code = code
            message = "remote listing failed safely"
        return code, redacted_code, message


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
