from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vendor_flat_files.options.options_day_aggs_inspector import DEFAULT_INSPECT_PATH, inspect_options_day_aggs_quarantine_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect the local options day aggregates quarantine file.")
    parser.add_argument("--input-path", default=str(DEFAULT_INSPECT_PATH), help="Local gzip CSV file path.")
    parser.add_argument("--sample-rows", type=int, default=3, help="Maximum number of safe sample rows to include.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = inspect_options_day_aggs_quarantine_file(input_path=args.input_path, sample_rows_limit=args.sample_rows)
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
