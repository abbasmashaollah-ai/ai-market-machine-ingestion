from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_local_handoff_generation_evidence.md")


def test_local_handoff_generation_evidence_contains_required_language() -> None:
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "This is evidence only.",
        "source quarantine file path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz`",
        "source quarantine file size: `317857`",
        "source quarantine file sha256: `ac71addad2e0ba969b76763585e7e15fc74660a13c80d31869b5cbf787df3682`",
        "date processed: `2026-06-15`",
        "parser/normalizer command: `python scripts/preview_polygon_stock_day_agg_warehouse_handoff_candidate.py --file outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz --date 2026-06-15 --sample-limit 5`",
        "handoff writer command: `python scripts/write_polygon_stock_day_agg_local_handoff_artifact.py --file outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz --date 2026-06-15 --output-dir outputs/handoff_candidates/polygon_stock_day_aggs --approve-local-handoff-write --approval-phrase APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE`",
        "batch handoff writer command: `python scripts/write_polygon_stock_day_agg_batch_local_handoff_artifacts.py --input-dir outputs/quarantine/polygon_flat_files --start-date 2026-06-15 --end-date 2026-06-15 --output-dir outputs/handoff_candidates/polygon_stock_day_aggs --approve-local-handoff-write --approval-phrase APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE`",
        "validator command: `python scripts/validate_polygon_stock_day_agg_local_handoff_artifacts.py --manifest outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json`",
        "intake package command: `python scripts/build_polygon_stock_day_agg_data_repo_intake_package.py --manifest outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json --output-dir outputs/intake_packages/polygon_stock_day_aggs`",
        "generated rows JSONL path: `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_rows.jsonl`",
        "generated summary JSON path: `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_summary.json`",
        "generated manifest path: `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json`",
        "generated intake package path: `outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_2026-06-15_intake_package.json`",
        "row count: `12235`",
        "symbol count: `12235`",
        "min trade date: `2026-06-15`",
        "max trade date: `2026-06-15`",
        "validation status: `validation_passed: true`",
        "no vendor call",
        "no download",
        "no data repo mutation",
            "No DB write",
        "no scheduler activation",
        "no production warehouse mutation",
        "no secrets printed",
        "The generated outputs are intentionally left uncommitted.",
        "The next step is data-repo intake validation and the production migration gate.",
    ]:
        assert phrase in text
