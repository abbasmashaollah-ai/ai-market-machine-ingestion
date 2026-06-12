from pathlib import Path


def test_system_review_ingestion_architecture_state_doc_contains_required_language() -> None:
    doc = Path("docs/system_review_ingestion_architecture_state.md").read_text(encoding="utf-8")

    required_phrases = [
        "REVIEW ONLY",
        "NO IMPLEMENTATION",
        "NO VENDOR CALLS",
        "NO DB WRITES",
        "ai-market-machine-ingestion",
        "three-system architecture",
        "producer",
        "handoff",
        "JSONL",
        "source_sha256",
        "producer_run_id",
        "lineage",
        "validation",
        "rejection",
        "OHLCV",
        "options",
        "News + Sentiment",
        "ai-market-machine-data",
        "AI Machine",
        "no runtime behavior changed",
        "no vendor calls",
        "no downloads",
        "no DB writes",
        "no scheduler activation",
        "no AI/trading/risk/regime/portfolio logic",
        "no secrets stored",
        "credential rotation still required",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in doc]

    assert not missing, f"Missing required phrases: {missing}"
