from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.features.breadth.breadth_jsonl_handoff_builder import (
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SCHEMA_VERSION,
    write_breadth_observations_handoff_jsonl,
)
from app.features.breadth.breadth_observation_builder import build_breadth_observation
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def _build_fixture_observation() -> dict[str, object]:
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}
    observation = build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")
    observation["source"] = "fixture_vendor"
    observation["source_dataset"] = "breadth_observations"
    observation["source_sha256"] = "fixture-source-sha256"
    observation["source_file"] = "fixtures/breadth/breadth.jsonl"
    observation["source_uri"] = "file:///fixtures/breadth/breadth.jsonl"
    observation["universe_name"] = "S&P 500"
    return observation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run breadth observations JSONL handoff locally.")
    parser.add_argument("--output-file", default=str(DEFAULT_OUTPUT_PATH), help="Local JSONL output path.")
    parser.add_argument("--quarantine-file", help="Optional quarantine JSONL output path.")
    parser.add_argument("--summary-only", action="store_true", help="Print a compact JSON summary only.")
    args = parser.parse_args(argv)

    observation = _build_fixture_observation()
    result = write_breadth_observations_handoff_jsonl(
        [observation],
        args.output_file,
        source_vendor="fixture_vendor",
        source_dataset="breadth_observations",
        source_sha256="fixture-source-sha256",
        schema_version=DEFAULT_SCHEMA_VERSION,
        generated_at="2026-01-15T16:00:00Z",
        quarantine_path=args.quarantine_file,
    )

    payload = {
        "input_row_count": result.records_received,
        "accepted_row_count": result.records_written,
        "rejected_quarantined_row_count": result.records_rejected,
        "validation_error_summary": [item["rejection_reasons"] for item in result.rejection_reasons],
        "idempotency_key_coverage": len(result.idempotency_keys) == result.records_written,
        "source_lineage_summary": result.lineage_summary,
        "schema_version": result.schema_version,
        "generated_artifact_path": result.output_path,
        "quarantine_path": result.quarantine_path,
        "no_vendor_calls": True,
        "no_db_writes": True,
        "no_scheduler_activation": True,
        "no_production_change": True,
    }
    if not args.summary_only:
        payload["records"] = json.loads(Path(result.output_path).read_text(encoding="utf-8"))
        if result.quarantine_path:
            payload["quarantined_records"] = json.loads(Path(result.quarantine_path).read_text(encoding="utf-8"))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
