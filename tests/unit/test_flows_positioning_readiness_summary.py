from __future__ import annotations

from pathlib import Path


def test_readiness_summary_exists_and_mentions_required_items():
    text = Path("docs/flows_positioning_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "vertical-slice plan exists",
        "source plan exists",
        "fixture-backed dry-run foundation exists",
        "preflight exists",
        "evidence plan exists",
        "manual inventory includes flows/positioning commands",
        "etf flows",
        "fund flows",
        "short interest",
        "institutional positioning",
        "cftc/cot positioning",
        "dark pool/off-exchange volume",
        "symbol_master",
        "etf/index universe",
        "fmp",
        "finra",
        "cftc",
        "etf issuer/public datasets",
        "vendor_flow_feed",
        "manual_fixture",
        "live adapters are not built yet",
        "data-side contracts are not yet approved",
        "persistence is deferred",
        "no db reads or db writes are enabled",
        "data-side flows/positioning contract",
        "finra short-interest live dry-run planning",
        "cftc/cot live dry-run planning",
        "etf issuer flow-source research",
    ]:
        assert needle in text


def test_future_build_order_pauses_flows_and_marks_planning_complete():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "flows/positioning" in text
    assert "paused at readiness checkpoint" in text
    assert "planning coverage complete" in text
    assert "next phase: data-side contracts and live-adapter prioritization" in text


def test_boundary_language_present():
    text = Path("docs/flows_positioning_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "producer-planning side only" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
