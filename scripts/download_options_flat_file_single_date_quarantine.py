from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import boto3  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - boto3 may be absent in some local environments.
    boto3 = None  # type: ignore[assignment]

from app.vendor_flat_files.options.options_flat_file_quarantine import (
    APPROVAL_PHRASE,
    DEFAULT_DATE,
    DEFAULT_LOCAL_RELATIVE_PATH,
    download_single_date_quarantine,
    options_output_path,
    redacted_options_tail,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded options single-date local quarantine download.")
    parser.add_argument("--date", default=DEFAULT_DATE, help="Date in YYYY-MM-DD format.")
    parser.add_argument("--quarantine-dir", default=str(DEFAULT_LOCAL_RELATIVE_PATH.parent), help="Local quarantine directory.")
    parser.add_argument("--approval-phrase", default="", help="Exact approval phrase required for download.")
    parser.add_argument("--approve-local-quarantine-download", action="store_true", help="Approve a single local quarantine download.")
    parser.add_argument("--overwrite-local-file", action="store_true", help="Overwrite an existing local file instead of skipping.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _safe_payload(*, enabled: bool, approval_phrase: str, date_value: str, quarantine_dir: str, overwrite_local_file: bool, env: dict[str, str] | None = None) -> dict[str, object]:
    payload = dict(
        download_single_date_quarantine(
            env=dict(env or os.environ),
            enabled=enabled,
            approval_phrase=approval_phrase,
            date_value=date_value,
            quarantine_dir=quarantine_dir,
            overwrite_local_file=overwrite_local_file,
            boto3_module=boto3,
        )
    )
    payload.update(
        {
            "approval_phrase_matched": bool(payload.get("approval_phrase_matched")),
            "approval_required": bool(payload.get("approval_required", True)),
            "redacted_key_tail": redacted_options_tail(date_value),
            "download_attempted": bool(payload.get("download_attempted")),
            "download_succeeded": bool(payload.get("download_succeeded")),
            "vendor_call_attempted": bool(payload.get("vendor_call_attempted")),
            "remote_head_object_attempted": bool(payload.get("remote_head_object_attempted")),
            "decompression_attempted": False,
            "parse_attempted": False,
            "export_attempted": False,
            "db_read_attempted": False,
            "db_write_attempted": False,
            "ingestion_attempted": False,
            "scheduler_activation_attempted": False,
            "production_mutation_attempted": False,
            "output_path": str(options_output_path(date_value, quarantine_dir)),
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    approval_matched = args.approval_phrase == APPROVAL_PHRASE
    payload = _safe_payload(
        enabled=approval_matched,
        approval_phrase=args.approval_phrase,
        date_value=args.date,
        quarantine_dir=args.quarantine_dir,
        overwrite_local_file=bool(args.overwrite_local_file),
    )
    safe_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(safe_json + "\n", encoding="utf-8")
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
