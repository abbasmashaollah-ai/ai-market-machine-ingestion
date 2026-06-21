from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_untracked_artifact_review_evidence.md")


def test_polygon_stock_day_agg_untracked_artifact_review_evidence_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "evidence doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Record read-only classification of untracked files before continuing Polygon daily update work.",
        "app/warehouse/news_sentiment_handoff_acceptance.py",
        "tests/warehouse/test_news_sentiment_handoff_acceptance.py",
        "These news_sentiment files are for another domain and are not part of the Polygon stock day aggregate freshness-remediation chain.",
        "Do not delete",
        "inspect separately under news/sentiment domain",
        "outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_rows.jsonl",
        "outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_summary.json",
        "outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-15_2026-06-15_manifest.json",
        "outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_2026-06-15_intake_package.json",
        "outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz",
        "do not stage; do not commit; preserve outside git or keep untouched until explicit artifact retention decision",
        "Generated outputs should not be committed",
        "Future `git add` commands must use explicit path allowlists only",
        "Accidental staging risk",
        "Stale artifact confusion risk",
        "Cross-domain drift risk",
        "Approval/execution confusion risk",
        "Polygon vendor probe approval work may continue only with explicit `git add -f` for docs/tests",
        "Do not stage `outputs/`",
        "Do not stage news_sentiment files",
        "Do not delete untracked files in this step",
        "total_rows_written` / rows = `12235`",
        "production_approved = false",
        "preview_or_local_handoff_only = true",
        "source_file_sha256 = ac71addad2e0ba969b76763585e7e15fc74660a13c80d31869b5cbf787df3682",
        "source_file_size_bytes = 317857",
        "No vendor call/listing/probe",
        "No download",
        "No scheduler/backfill",
        "No DB write",
        "No data repo mutation",
        "No production staging load",
        "No canonical promotion",
        "No AI wiring",
        "No generated output commit",
    ]:
        assert phrase in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key",
    ]:
        assert forbidden not in lowered
