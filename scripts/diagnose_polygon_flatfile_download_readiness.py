from __future__ import annotations

import argparse
import os


def _configured(value: str | None) -> bool:
    return bool(value and value.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Polygon flat-file download readiness without connecting to vendors.")
    parser.add_argument("--dataset", default="ohlcv", help="Dataset name, default ohlcv.")
    parser.add_argument("--asset-class", default="stocks", help="Asset class, default stocks.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--storage-root", default=None, help="Optional storage root.")
    args = parser.parse_args()

    storage_root_configured = _configured(args.storage_root) or _configured(os.environ.get("POLYGON_FLATFILE_STORAGE_ROOT"))

    print("source_mode=flatfiles")
    print(f"dataset={args.dataset}")
    print(f"asset_class={args.asset_class}")
    print(f"timeframe={args.timeframe}")
    print("download_enabled=false")
    print("download_mode=dry_run_planning_only")
    print("official_layout_required=true")
    print("credentials_required=true")
    print(f"storage_root_configured={'true' if storage_root_configured else 'false'}")
    print("manifest_required=true")
    print("integrity_required=true")
    print("quarantine_required=true")
    print("parse_after_download=false")
    print("download_readiness_status=planning_only_not_enabled")
    print(
        "required_before_download_enablement=official_layout_verified, config_configured_but_disabled, storage_policy_reviewed, manifest_write_enabled, integrity_policy_defined, quarantine_policy_defined"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
