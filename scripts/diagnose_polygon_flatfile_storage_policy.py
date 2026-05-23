from __future__ import annotations

import argparse
import os
from pathlib import Path


FORBIDDEN_LOCATIONS = ("repo_root", "app", "scripts", "tests", "docs")
ALLOWED_FUTURE_SUBDIRS = ("raw", "staging", "parsed", "quarantine", "manifests")


def _configured(value: str | None) -> bool:
    return bool(value and value.strip())


def _source_for_storage_root(cli_storage_root: str | None) -> tuple[str, str | None]:
    if _configured(cli_storage_root):
        return "cli", cli_storage_root
    env_storage_root = os.environ.get("POLYGON_FLATFILE_STORAGE_ROOT")
    if _configured(env_storage_root):
        return "env", env_storage_root
    return "none", None


def _is_within_repo_source_folder(storage_root: str) -> bool:
    normalized = Path(storage_root).as_posix().lower()
    return any(f"/{folder}/" in f"/{normalized}/" for folder in FORBIDDEN_LOCATIONS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file storage policy without touching storage.")
    parser.add_argument("--storage-root", default=None, help="Optional storage root path string.")
    args = parser.parse_args()

    storage_root_source, storage_root_value = _source_for_storage_root(args.storage_root)
    storage_root_configured = storage_root_source != "none"
    storage_policy_status = "planning_only_not_enabled"
    if storage_root_value and _is_within_repo_source_folder(storage_root_value):
        storage_policy_status = "manual_review_needed"

    print(f"storage_root_configured={'true' if storage_root_configured else 'false'}")
    print(f"storage_root_source={storage_root_source}")
    print(f"storage_policy_status={storage_policy_status}")
    print("writes_enabled=false")
    print(f"allowed_future_subdirs={','.join(ALLOWED_FUTURE_SUBDIRS)}")
    print(f"forbidden_locations={','.join(FORBIDDEN_LOCATIONS)}")
    print("cleanup_policy_required=true")
    print("checksum_policy_required=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
