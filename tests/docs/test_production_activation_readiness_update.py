from __future__ import annotations

from pathlib import Path


ALLOWED_VERDICTS = {
    "READY_FOR_LIMITED_PRODUCTION_ACTIVATION",
    "NOT_READY_FOR_PRODUCTION_ACTIVATION",
    "READY_ONLY_FOR_CONTROLLED_SINGLE_SYMBOL_PRODUCTION_PROBE",
    "READY_ONLY_FOR_SAFE_DB_WRITE_VERIFICATION",
}


def test_production_activation_readiness_update_exists_and_contains_required_sections() -> None:
    path = Path("docs/production_activation_readiness_update.md")
    assert path.exists(), "docs/production_activation_readiness_update.md must exist"
    text = path.read_text(encoding="utf-8")

    assert "Executive Verdict" in text
    assert any(verdict in text for verdict in ALLOWED_VERDICTS)
    assert "Production Blockers" in text
    assert "First Real Production Candidate" in text
    assert "Required Pre-Production Checklist" in text
    assert "Recommended Next Command" in text
    assert "No production action was performed in this update" in text
    assert "No live vendor call was performed in this update" in text
    assert "No production DB write was performed in this update" in text
    assert "Do not run 10,000+ ticker ingestion yet" in text
    assert "Do not activate unattended scheduler execution yet" in text
    assert "The next step must be a production activation decision, not another dry-run loop" in text

