from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
