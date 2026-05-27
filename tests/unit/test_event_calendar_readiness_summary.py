from __future__ import annotations

from pathlib import Path


def test_event_calendar_readiness_summary_exists_and_mentions_verified_state() -> None:
    text = Path("docs/event_calendar_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "canonical event-calendar contract exists in `ai-market-machine-data`",
        "dry-run foundation exists",
        "source plan exists",
        "preflight exists",
        "evidence plan exists",
        "writer plan exists, but persistence remains deferred",
        "opex deterministic slice is verified",
        "cpi/fomc/nfp macro-event fixture foundation exists",
        "macro-event source plan exists",
        "live bls and federal reserve adapters are not built yet",
        "no db writes are enabled",
    ]:
        assert needle in text


def test_event_calendar_readiness_summary_boundary_language() -> None:
    text = Path("docs/event_calendar_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "no vendor calls are made by this summary" in text
    assert "no scheduler, fastapi route, migration, schema ownership, ai, trading, risk, signal, regime, or portfolio logic belongs here" in text


def test_event_calendar_readiness_summary_next_options() -> None:
    text = Path("docs/event_calendar_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "bls live dry-run" in text
    assert "federal reserve fomc dry-run" in text
    assert "earnings calendar plan" in text
    assert "earnings calendar vertical slice planning" in text

