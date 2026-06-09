from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vendor_flat_files.options.options_day_aggs_handoff_builder import (
    APPROVAL_PHRASE,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SAMPLE_LIMIT,
    MAX_SAMPLE_LIMIT,
    build_options_day_aggs_handoff_sample,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a local options day aggregates sample handoff artifact. "
            f"Requires the exact approval phrase: {APPROVAL_PHRASE}"
        )
    )
    parser.add_argument("--approval-phrase", default="", help="Exact approval phrase required to write the sample artifact.")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT_PATH), help="Local quarantine gzip CSV path.")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH), help="Local sample handoff jsonl path.")
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT, help="Sample size cap, max 1000.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = build_options_day_aggs_handoff_sample(
        approval_phrase=args.approval_phrase,
        input_path=args.input_path,
        output_path=args.output_path,
        requested_sample_limit=min(args.sample_limit, MAX_SAMPLE_LIMIT),
    )
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
