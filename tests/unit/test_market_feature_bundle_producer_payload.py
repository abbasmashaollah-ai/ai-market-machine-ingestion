from __future__ import annotations

import ast
import json
from pathlib import Path

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_producer_payload import build_market_feature_bundle_producer_payload


def _bundle() -> dict:
    return run_market_feature_bundle_dry_run(observation_date="2026-01-15", timestamp="2026-01-15T12:00:00Z")


def test_market_feature_bundle_producer_payload_contains_required_fields() -> None:
    payload = build_market_feature_bundle_producer_payload(
        _bundle(),
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )

    for key in [
        "observation_date",
        "generated_at",
        "universe",
        "schema_version",
        "dataset_version",
        "idempotency_key",
        "raw_sections",
        "synthesized_sections",
        "section_record_counts",
        "section_labels",
        "compact_summary",
        "full_bundle_payload",
        "validation_status",
        "validation_errors",
        "validation_warnings",
        "total_warnings",
        "safety_flags",
        "rejected_counts",
        "certification_status",
        "source_repo",
        "source_run_id",
        "input_dataset_versions",
        "lineage_refs",
        "quality_result_refs",
    ]:
        assert key in payload


def test_market_feature_bundle_producer_payload_is_json_serializable() -> None:
    payload = build_market_feature_bundle_producer_payload(
        _bundle(),
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )

    json.dumps(payload, sort_keys=True)


def test_market_feature_bundle_producer_payload_maps_sections_and_summary() -> None:
    payload = build_market_feature_bundle_producer_payload(
        _bundle(),
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )

    assert payload["raw_sections"] == [
        "prices",
        "breadth",
        "sector_rotation",
        "cross_asset",
        "liquidity_rates",
        "volatility",
        "event_calendar",
        "news_sentiment",
        "earnings",
        "fundamentals",
        "flows_positioning",
        "options",
    ]
    assert payload["synthesized_sections"] == ["macro_liquidity", "market_risk", "market_regime"]
    assert payload["compact_summary"]["total_warnings"] == payload["total_warnings"]
    assert payload["full_bundle_payload"]["observation_date"] == "2026-01-15"


def test_market_feature_bundle_producer_payload_defaults_and_certification() -> None:
    payload = build_market_feature_bundle_producer_payload(
        _bundle(),
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )

    assert payload["source_repo"] == "ai-market-machine-ingestion"
    assert payload["source_run_id"] is None
    assert payload["input_dataset_versions"] == {}
    assert payload["lineage_refs"] == []
    assert payload["quality_result_refs"] == []
    assert payload["certification_status"] == "CERTIFIED"


def test_market_feature_bundle_producer_payload_idempotency_is_deterministic_and_sensitive() -> None:
    base_bundle = _bundle()
    payload_a = build_market_feature_bundle_producer_payload(
        base_bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )
    payload_b = build_market_feature_bundle_producer_payload(
        base_bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )
    payload_c = build_market_feature_bundle_producer_payload(
        base_bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
        dataset_version="fixture.v2",
    )
    altered_bundle = dict(base_bundle)
    altered_bundle["warnings"] = list(altered_bundle["warnings"]) + ["extra-warning"]
    payload_d = build_market_feature_bundle_producer_payload(
        altered_bundle,
        observation_date="2026-01-15",
        generated_at="2026-01-15T12:34:56Z",
    )

    assert payload_a["idempotency_key"] == payload_b["idempotency_key"]
    assert payload_a["idempotency_key"] != payload_c["idempotency_key"]
    assert payload_a["idempotency_key"] != payload_d["idempotency_key"]


def test_market_feature_bundle_producer_payload_module_has_no_writer_or_runtime_references() -> None:
    source = Path("app/features/market_features/market_feature_bundle_producer_payload.py").read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    import_names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name.lower())
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_names.add(node.module.lower())
            for alias in node.names:
                import_names.add(alias.name.lower())

    for forbidden in [
        "canonicalwriter",
        "ingestionrunstore",
        "dataqualityresultstore",
        "datalineagestore",
        "session",
        "engine",
        "vendor",
        "scheduler",
        "writer",
    ]:
        assert forbidden not in import_names
