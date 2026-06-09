from __future__ import annotations

OPTIONS_PREFIX = "us_options_opra/day_aggs_v1"
OPTIONS_SAMPLE_DATE = "2025-11-05"
OPTIONS_SAMPLE_KEY = f"{OPTIONS_PREFIX}/2025/11/2025-11-05.csv.gz"
OPTIONS_CONFIG_NAMES = (
    "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
    "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
    "POLYGON_FLAT_FILE_ENDPOINT",
    "POLYGON_FLAT_FILE_BUCKET",
)


def redacted_key_tail(key: str) -> str:
    parts = key.split("/")
    if len(parts) >= 2 and parts[-1].endswith(".csv.gz"):
        return f"{parts[-2]}/{parts[-1]}"
    return ""


def is_config_complete(env: dict[str, str]) -> bool:
    return all(env.get(name) for name in OPTIONS_CONFIG_NAMES)


def present_names(env: dict[str, str]) -> list[str]:
    return [name for name in OPTIONS_CONFIG_NAMES if env.get(name)]


def missing_names(env: dict[str, str]) -> list[str]:
    return [name for name in OPTIONS_CONFIG_NAMES if not env.get(name)]


def classify_config(env: dict[str, str]) -> str:
    present = present_names(env)
    if len(present) == len(OPTIONS_CONFIG_NAMES):
        return "polygon_flat_file"
    if present:
        return "ambiguous"
    return "missing"
