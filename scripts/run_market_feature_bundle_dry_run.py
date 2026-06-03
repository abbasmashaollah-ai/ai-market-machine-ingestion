from __future__ import annotations

import argparse
import json
import sys

from app.features.market_feature_bundle import run_market_feature_bundle_dry_run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the market feature bundle dry run and print JSON output.")
    parser.add_argument("--observation-date", default=None, help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--timestamp", default=None, help="Optional ISO 8601 timestamp.")
    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    observation_date = args.observation_date or "2026-01-15"
    bundle = run_market_feature_bundle_dry_run(observation_date=observation_date, timestamp=args.timestamp)
    json.dump(bundle, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())