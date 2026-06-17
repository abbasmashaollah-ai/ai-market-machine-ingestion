from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.write_polygon_stock_day_agg_local_handoff_artifact import (
    APPROVAL_PHRASE,
    ALLOWED_OUTPUT_ROOT,
    write_polygon_stock_day_agg_local_handoff_artifact,
)

DEFAULT_INPUT_DIR = Path("outputs/quarantine/polygon_flat_files")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write local-only Polygon stock day aggregates handoff artifacts in batch.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Local quarantine input directory.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--output-dir", required=True, help="Local output directory under outputs/handoff_candidates/polygon_stock_day_aggs/.")
    parser.add_argument("--approve-local-handoff-write", action="store_true", help="Explicit approval flag required for local writes.")
    parser.add_argument("--approval-phrase", default="", help="Required approval phrase.")
    return parser


def _validate_output_dir(output_dir: Path) -> tuple[bool, str]:
    try:
        resolved = output_dir.resolve()
        allowed = ALLOWED_OUTPUT_ROOT.resolve()
        if resolved == allowed or allowed in resolved.parents:
            return True, ""
        return False, f"output_dir must be within {ALLOWED_OUTPUT_ROOT.as_posix()}"
    except Exception:
        return False, "output_dir could not be resolved safely"


def _iter_dates(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        return []
    values = []
    current = start
    while current <= end:
        values.append(current.isoformat())
        current += timedelta(days=1)
    return values


def write_polygon_stock_day_agg_batch_local_handoff_artifacts(
    *,
    input_dir: str | Path,
    start_date: str,
    end_date: str,
    output_dir: str | Path,
    approve_local_handoff_write: bool,
    approval_phrase: str,
) -> dict[str, Any]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    payload: dict[str, Any] = {
        "start_date": start_date,
        "end_date": end_date,
        "requested_date_count": 0,
        "local_files_found_count": 0,
        "local_files_missing_count": 0,
        "dates_processed": [],
        "dates_missing": [],
        "total_rows_written": 0,
        "total_rows_rejected": 0,
        "per_date_outputs": [],
        "output_root": str(output_dir),
        "approval_phrase_matched": False,
        "local_handoff_write_authorized": False,
        "production_approved": False,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "blockers": [
            "batch local-only handoff artifact writer is allowed only after explicit approval",
            "no vendor calls, downloads, DB writes, ingestion, scheduler activation, or production mutation are permitted",
        ],
    }

    output_ok, output_error = _validate_output_dir(output_dir)
    if not output_ok:
        payload["blockers"].append(output_error)
        return payload
    if not approve_local_handoff_write or approval_phrase != APPROVAL_PHRASE:
        payload["blockers"].append("missing or incorrect approval phrase")
        return payload

    dates = _iter_dates(start_date, end_date)
    payload["requested_date_count"] = len(dates)
    payload["approval_phrase_matched"] = True
    payload["local_handoff_write_authorized"] = True
    output_dir.mkdir(parents=True, exist_ok=True)

    for requested_date in dates:
        input_path = input_dir / f"polygon_stocks_day_aggs_{requested_date}.csv.gz"
        if not input_path.exists():
            payload["dates_missing"].append(requested_date)
            continue
        payload["dates_processed"].append(requested_date)
        payload["local_files_found_count"] += 1
        result = write_polygon_stock_day_agg_local_handoff_artifact(
            input_path=input_path,
            requested_date=requested_date,
            output_dir=output_dir,
            approve_local_handoff_write=True,
            approval_phrase=APPROVAL_PHRASE,
        )
        payload["total_rows_written"] += int(result.get("row_count_written", 0))
        payload["total_rows_rejected"] += int(result.get("rejected_row_count", 0))
        payload["per_date_outputs"].append(
            {
                "requested_date": requested_date,
                "summary_path": result.get("output_summary_path"),
                "rows_path": result.get("output_rows_path"),
                "row_count_written": result.get("row_count_written", 0),
                "rejected_row_count": result.get("rejected_row_count", 0),
            }
        )

    payload["local_files_missing_count"] = len(dates) - payload["local_files_found_count"]
    manifest_path = output_dir / f"polygon_stock_day_aggs_batch_{start_date}_{end_date}_manifest.json"
    payload["manifest_path"] = str(manifest_path)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["manifest_exists"] = manifest_path.exists()
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = write_polygon_stock_day_agg_batch_local_handoff_artifacts(
        input_dir=args.input_dir,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
        approve_local_handoff_write=args.approve_local_handoff_write,
        approval_phrase=args.approval_phrase,
    )
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
