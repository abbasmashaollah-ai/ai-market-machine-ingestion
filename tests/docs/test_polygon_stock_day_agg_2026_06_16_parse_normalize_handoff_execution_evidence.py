from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_parse_normalize_handoff_execution_evidence.md")


def test_polygon_stock_day_agg_2026_06_16_parse_normalize_handoff_execution_evidence_contains_required_language() -> None:
    assert DOC_PATH.exists(), "execution evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")
    lowered = text.lower()

    for phrase in [
        "Parse/normalize/handoff approval package commit: `5d15d08`",
        "Parse/normalize/handoff operator approval record commit: `56e10bb`",
        "Quarantine download evidence commit: `d4b4896`",
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 PARSE NORMALIZE HANDOFF",
        "Path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "Size_bytes: `316221`",
        "Sha256: `9f40f8beb445623aa77f3a2f9fa721ae7f7fa99c27021df683bc8044f9f2b0a1`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_rows.jsonl`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_summary.json`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-16_2026-06-16_manifest.json`",
        "`outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_2026-06-16_intake_package.json`",
        "Row count: `12257`",
        "Symbol count: `12255`",
        "Rejected row count: `0`",
        "Source file sha256 carried forward: `9f40f8beb445623aa77f3a2f9fa721ae7f7fa99c27021df683bc8044f9f2b0a1`",
        "vendor_call_attempted",
        "remote_read_attempted",
        "download_attempted",
        "this evidence records the approved local parse, normalization, and handoff generation execution only.",
        "generated outputs remain uncommitted unless separately approved",
        "the `2026-06-15` generated outputs were not overwritten by the successful `2026-06-16` execution path",
        "move to the `ai-market-machine-data` intake validation approval package for the generated `2026-06-16` intake package",
        "no data repo mutation is authorized by this evidence",
        "vendor call, remote read, and download were not used in this local execution",
    ]:
        assert phrase.lower() in lowered

    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
