from __future__ import annotations

import importlib.util
import json
import os
from dataclasses import dataclass
from typing import Any

from app.vendor_flat_files.polygon_flat_file_adapter import REQUIRED_CONFIG_NAMES

SAFE_REQUIRED_CONFIG_KEYS = REQUIRED_CONFIG_NAMES


@dataclass(frozen=True, slots=True)
class ProbeEnvironmentReadinessResult:
    readiness_passed: bool
    boto3_available: bool
    boto3_error_type: str | None
    required_config_keys_present: tuple[str, ...]
    required_config_keys_missing: tuple[str, ...]
    accepted_config_alternatives: tuple[str, ...]
    vendor_call_attempted: bool
    remote_listing_attempted: bool
    download_attempted: bool
    file_write_attempted: bool
    secrets_printed: bool
    safe_to_retry_probe: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "readiness_passed": self.readiness_passed,
            "boto3_available": self.boto3_available,
            "boto3_error_type": self.boto3_error_type,
            "required_config_keys_present": list(self.required_config_keys_present),
            "required_config_keys_missing": list(self.required_config_keys_missing),
            "accepted_config_alternatives": list(self.accepted_config_alternatives),
            "vendor_call_attempted": self.vendor_call_attempted,
            "remote_listing_attempted": self.remote_listing_attempted,
            "download_attempted": self.download_attempted,
            "file_write_attempted": self.file_write_attempted,
            "secrets_printed": self.secrets_printed,
            "safe_to_retry_probe": self.safe_to_retry_probe,
        }


def _import_boto3_available() -> tuple[bool, str | None]:
    try:
        return importlib.util.find_spec("boto3") is not None, None
    except Exception as exc:  # pragma: no cover - defensive only
        return False, type(exc).__name__


def check_probe_environment_readiness(env: dict[str, str] | None = None) -> ProbeEnvironmentReadinessResult:
    env_map = dict(env or os.environ)
    boto3_available, boto3_error_type = _import_boto3_available()
    present = tuple(name for name in SAFE_REQUIRED_CONFIG_KEYS if env_map.get(name))
    missing = tuple(name for name in SAFE_REQUIRED_CONFIG_KEYS if not env_map.get(name))
    accepted_alternatives = tuple()
    readiness_passed = boto3_available and not missing
    return ProbeEnvironmentReadinessResult(
        readiness_passed=readiness_passed,
        boto3_available=boto3_available,
        boto3_error_type=boto3_error_type,
        required_config_keys_present=present,
        required_config_keys_missing=missing,
        accepted_config_alternatives=accepted_alternatives,
        vendor_call_attempted=False,
        remote_listing_attempted=False,
        download_attempted=False,
        file_write_attempted=False,
        secrets_printed=False,
        safe_to_retry_probe=readiness_passed,
    )


def render_probe_environment_readiness_json(env: dict[str, str] | None = None) -> str:
    return json.dumps(check_probe_environment_readiness(env).to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
