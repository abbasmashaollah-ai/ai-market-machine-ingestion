from __future__ import annotations

import os


ENV_VARS = (
    "POLYGON_FLATFILE_ACCESS_KEY_ID",
    "POLYGON_FLATFILE_SECRET_ACCESS_KEY",
    "POLYGON_FLATFILE_BUCKET",
    "POLYGON_FLATFILE_ENDPOINT",
    "POLYGON_FLATFILE_REGION",
    "POLYGON_FLATFILE_STORAGE_ROOT",
)


def _configured(name: str) -> bool:
    value = os.environ.get(name)
    return bool(value and value.strip())


def main() -> int:
    access_key_configured = _configured("POLYGON_FLATFILE_ACCESS_KEY_ID")
    secret_key_configured = _configured("POLYGON_FLATFILE_SECRET_ACCESS_KEY")
    bucket_configured = _configured("POLYGON_FLATFILE_BUCKET")
    endpoint_configured = _configured("POLYGON_FLATFILE_ENDPOINT")
    region_configured = _configured("POLYGON_FLATFILE_REGION")
    storage_root_configured = _configured("POLYGON_FLATFILE_STORAGE_ROOT")

    configured_count = sum(
        (
            access_key_configured,
            secret_key_configured,
            bucket_configured,
            endpoint_configured,
            region_configured,
            storage_root_configured,
        )
    )
    if configured_count == 0:
        config_readiness_status = "not_configured"
    elif configured_count == len(ENV_VARS):
        config_readiness_status = "configured_but_disabled"
    else:
        config_readiness_status = "partial_configured"

    print(f"access_key_configured={'true' if access_key_configured else 'false'}")
    print(f"secret_key_configured={'true' if secret_key_configured else 'false'}")
    print(f"bucket_configured={'true' if bucket_configured else 'false'}")
    print(f"endpoint_configured={'true' if endpoint_configured else 'false'}")
    print(f"region_configured={'true' if region_configured else 'false'}")
    print(f"storage_root_configured={'true' if storage_root_configured else 'false'}")
    print(f"config_readiness_status={config_readiness_status}")
    print("flatfile_download_enabled=false")
    print("flatfile_discovery_enabled=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
