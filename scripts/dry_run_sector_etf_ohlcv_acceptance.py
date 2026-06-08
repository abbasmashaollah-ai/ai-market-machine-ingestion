from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.warehouse.sector_etf_ohlcv_acceptance_service import (
    SECTOR_ETF_UNIVERSE,
    accept_sector_etf_ohlcv_handoff_records,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local dry-run sector ETF OHLCV acceptance check.")
    parser.add_argument("--approved-candidate-test-mode", action="store_true", help="Use approved candidate dry-run shape instead of fixture-only shape.")
    parser.add_argument("--output-file", default=None, help="Optional output file for the safe summary JSON.")
    return parser


def _synthetic_records(*, approved_candidate_test_mode: bool) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, symbol in enumerate(SECTOR_ETF_UNIVERSE, start=1):
        cert_status = "APPROVED_CANDIDATE" if approved_candidate_test_mode else "FIXTURE_ONLY"
        records.append(
            {
                "symbol": symbol,
                "timestamp": "2026-01-15T00:00:00+00:00",
                "open": 100.0 + index,
                "high": 101.0 + index,
                "low": 99.0 + index,
                "close": 100.5 + index,
                "volume": 1_000_000 + index,
                "timeframe": "1d",
                "adjusted": True,
                "source": "synthetic_local",
                "dataset_version": "synthetic.v1",
                "schema_version": "canonical_ohlcv.v1",
                "validation_status": "PASS",
                "certification_status": cert_status,
                "lineage_id": f"synthetic-{symbol.lower()}-2026-01-15",
                "source_file_sha256": f"{symbol.lower()}-sha256-prefix",
                "idempotency_key": f"{symbol.lower()}-handoff-key-{index:02d}",
            }
        )
    return records


def _safe_summary(result) -> dict[str, object]:
    return {
        "records_received": result.records_received,
        "accepted_count": result.accepted_count,
        "rejected_count": result.rejected_count,
        "duplicate_count": result.duplicate_count,
        "symbols_accepted": list(result.symbols_accepted),
        "symbols_rejected": list(result.symbols_rejected),
        "validation_status": result.validation_status,
        "production_write_attempted": False,
        "db_write_attempted": False,
        "vendor_call_attempted": False,
        "scheduler_activation_attempted": False,
        "idempotency_key_prefixes": list(result.idempotency_key_prefixes),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    result = accept_sector_etf_ohlcv_handoff_records(
        _synthetic_records(approved_candidate_test_mode=args.approved_candidate_test_mode),
        approved_candidate_test_mode=args.approved_candidate_test_mode,
    )
    payload = json.dumps(_safe_summary(result), ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
