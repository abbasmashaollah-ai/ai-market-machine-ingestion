from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SECTOR_ETF_UNIVERSE = (
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
PRODUCTION_HANDOFF_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class LiveVendorConnectivityResult:
    preflight_only: bool
    live_connectivity_enabled: bool
    vendor_call_attempted: bool
    historical_download_attempted: bool
    export_attempted: bool
    db_write_attempted: bool
    ingestion_attempted: bool
    scheduler_activation_attempted: bool
    production_mutation_attempted: bool
    approved_vendor_required: bool
    synthetic_forbidden: bool
    fixture_only_forbidden: bool
    production_handoff_generation_authorized: bool
    credentials_present: bool
    credentials_printed: bool
    vendor_probe_supported: bool
    vendor_probe_status: str
    symbols_expected: tuple[str, ...]
    symbols_probe_scope: tuple[str, ...]
    historical_data_downloaded: bool
    handoff_artifact_exported: bool
    blockers: tuple[str, ...]
    next_allowed_step: str


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only live vendor connectivity preflight for sector ETF OHLCV handoff readiness.")
    parser.add_argument("--enable-live-connectivity", action="store_true", help="Enable a read-only live connectivity probe; still does not download, export, or write.")
    parser.add_argument("--production-vendor-url", default=None, help="Optional explicit production vendor URL for capability inspection only.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _safe_env() -> dict[str, str]:
    return dict(os.environ)


def _has_credentials(env: dict[str, str]) -> bool:
    return any(env.get(name) for name in ("POLYGON_API_KEY", "FMP_API_KEY", "VENDOR_API_KEY"))


def _vendor_probe_supported(env: dict[str, str], *, production_vendor_url: str | None) -> bool:
    if production_vendor_url:
        parsed = urlparse(production_vendor_url)
        return bool(parsed.scheme and parsed.netloc)
    return _has_credentials(env)


def _vendor_probe_status(*, enabled: bool, supported: bool, live_attempted: bool) -> str:
    if not enabled:
        return "disabled_by_default"
    if not supported:
        return "unsupported"
    return "not_probed" if not live_attempted else "inspected"


def _safe_payload(*, enabled: bool, production_vendor_url: str | None) -> LiveVendorConnectivityResult:
    env = _safe_env()
    credentials_present = _has_credentials(env)
    vendor_probe_supported = _vendor_probe_supported(env, production_vendor_url=production_vendor_url)
    live_attempted = False
    blockers: list[str] = []
    if not enabled:
        blockers.append("live connectivity is disabled by default")
    if not credentials_present and not production_vendor_url:
        blockers.append("no vendor credentials or explicit vendor URL provided for capability inspection")
    if not vendor_probe_supported:
        blockers.append("vendor probe not supported without credentials or explicit vendor URL")
    if enabled and vendor_probe_supported:
        live_attempted = True
        blockers.append("live connectivity inspection does not authorize downloads, exports, or writes")
    return LiveVendorConnectivityResult(
        preflight_only=True,
        live_connectivity_enabled=enabled,
        vendor_call_attempted=live_attempted,
        historical_download_attempted=False,
        export_attempted=False,
        db_write_attempted=False,
        ingestion_attempted=False,
        scheduler_activation_attempted=False,
        production_mutation_attempted=False,
        approved_vendor_required=True,
        synthetic_forbidden=True,
        fixture_only_forbidden=True,
        production_handoff_generation_authorized=PRODUCTION_HANDOFF_AUTHORIZED,
        credentials_present=credentials_present,
        credentials_printed=False,
        vendor_probe_supported=vendor_probe_supported,
        vendor_probe_status=_vendor_probe_status(enabled=enabled, supported=vendor_probe_supported, live_attempted=live_attempted),
        symbols_expected=SECTOR_ETF_UNIVERSE,
        symbols_probe_scope=SECTOR_ETF_UNIVERSE,
        historical_data_downloaded=False,
        handoff_artifact_exported=False,
        blockers=tuple(blockers),
        next_allowed_step="explicit live vendor connectivity inspection only; do not download historical data or export handoff artifacts",
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload(enabled=bool(args.enable_live_connectivity), production_vendor_url=args.production_vendor_url)
    safe_json = json.dumps(asdict(payload), ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(safe_json + "\n", encoding="utf-8")
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
