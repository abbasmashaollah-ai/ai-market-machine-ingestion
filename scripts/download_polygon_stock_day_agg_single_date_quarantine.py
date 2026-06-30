from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.download_polygon_flat_file_single_date_quarantine as base_cli

APPROVAL_PHRASE = "APPROVE POLYGON STOCK DAY AGG 2026-06-26 QUARANTINE DOWNLOAD"
APPROVED_DATE = "2026-06-26"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guarded Polygon stock day aggregate single-date local quarantine download.")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format.")
    parser.add_argument("--quarantine-dir", default=str(base_cli.DEFAULT_QUARANTINE_DIR), help="Local quarantine directory.")
    parser.add_argument("--approve-local-quarantine-download", action="store_true", help="Approve a single local quarantine download.")
    parser.add_argument("--approval-phrase", default="", help="Exact approval phrase required for download.")
    parser.add_argument("--overwrite-local-file", action="store_true", help="Overwrite an existing local file instead of skipping.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _safe_payload(*, enabled: bool, approval_phrase: str, date_value: str, quarantine_dir: str, overwrite_local_file: bool) -> dict[str, object]:
    if date_value != APPROVED_DATE:
        payload = base_cli._safe_payload(
            enabled=False,
            approval_phrase=approval_phrase,
            value=date_value,
            quarantine_dir=quarantine_dir,
            overwrite_local_file=overwrite_local_file,
            required_approval_phrase=APPROVAL_PHRASE,
        )
        payload["blockers"] = list(payload.get("blockers", [])) + ["date does not match the approved stock day aggregate target"]
        payload["approved_date"] = APPROVED_DATE
        payload["date_authorized"] = False
        return payload

    payload = base_cli._safe_payload(
        enabled=enabled,
        approval_phrase=approval_phrase,
        value=date_value,
        quarantine_dir=quarantine_dir,
        overwrite_local_file=overwrite_local_file,
        required_approval_phrase=APPROVAL_PHRASE,
    )
    payload["approved_date"] = APPROVED_DATE
    payload["date_authorized"] = bool(enabled and approval_phrase == APPROVAL_PHRASE)
    payload.setdefault("normalization_attempted", False)
    payload.setdefault("handoff_generation_attempted", False)
    payload.setdefault("intake_package_generation_attempted", False)
    payload.setdefault("db_write_attempted", False)
    payload.setdefault("data_repo_mutation_attempted", False)
    payload.setdefault("scheduler_activation_attempted", False)
    payload.setdefault("backfill_attempted", False)
    payload.setdefault("ai_wiring_attempted", False)
    payload.setdefault("generated_output_commit_attempted", False)
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload(
        enabled=bool(args.approve_local_quarantine_download),
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
