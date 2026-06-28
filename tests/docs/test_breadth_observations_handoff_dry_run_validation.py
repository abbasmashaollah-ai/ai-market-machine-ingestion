from pathlib import Path


DOC = Path("docs/breadth_observations_handoff_dry_run_validation.md")


def test_breadth_observations_handoff_dry_run_validation_doc_exists() -> None:
    assert DOC.exists()


def test_breadth_observations_handoff_dry_run_validation_doc_has_required_language() -> None:
    text = DOC.read_text(encoding="utf-8")
    required_phrases = [
        "Breadth Observations Handoff Dry-Run Validation",
        "local JSONL handoff artifact",
        "outputs/handoff/breadth/",
        "required contract-facing fields are present",
        "Deterministic idempotency keys are stable",
        "Invalid rows are rejected and can be quarantined locally",
        "Derived and signal fields remain excluded",
        "input row count",
        "accepted row count",
        "rejected/quarantined row count",
        "validation error summary",
        "idempotency key coverage",
        "source lineage summary",
        "generated artifact path",
        "No vendor call was made",
        "no production rollout is approved",
    ]
    for phrase in required_phrases:
        assert phrase in text
