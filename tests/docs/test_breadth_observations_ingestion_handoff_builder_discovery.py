from pathlib import Path


DOC = Path("docs/breadth_observations_ingestion_handoff_builder_discovery.md")


def test_breadth_observations_ingestion_handoff_builder_discovery_doc_exists() -> None:
    assert DOC.exists()


def test_breadth_observations_ingestion_handoff_builder_discovery_sections_present() -> None:
    text = DOC.read_text(encoding="utf-8")
    required_sections = [
        "# Breadth Observations Ingestion Handoff Builder Discovery",
        "## Status",
        "## Purpose",
        "## Repository Evidence Review",
        "## What Already Exists In Ingestion?",
        "## Current Stage Assessment",
        "## Is There Already A Breadth Observations JSONL Handoff Builder?",
        "## Contract Alignment Review",
        "## What Should Not Be Built Here",
        "## Exact Next Recommendation",
        "## Production Statement",
    ]
    for section in required_sections:
        assert section in text


def test_breadth_observations_ingestion_handoff_builder_discovery_records_key_findings() -> None:
    text = DOC.read_text(encoding="utf-8")
    expected_phrases = [
        "Runtime Production-shaped",
        "Runtime Partial",
        "Dry-run only",
        "Planning-only",
        "Tested",
        "Not Found",
        "No, not found.",
        "observation_date",
        "universe_key",
        "source_vendor",
        "source_dataset",
        "source_sha256",
        "advancing_volume",
        "declining_volume",
        "new_highs",
        "new_lows",
        "schema_version",
        "metadata",
        "idempotency",
        "quarantine",
        "Implement Breadth Observations JSONL Handoff Builder.",
        "No vendor call was made",
        "no production rollout is approved",
    ]
    for phrase in expected_phrases:
        assert phrase in text
