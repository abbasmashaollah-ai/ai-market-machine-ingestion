from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from app.vendor_flat_files.local_ohlcv_parser import parse_local_ohlcv_fixture
from app.vendor_flat_files.ohlcv_handoff_builder import build_ohlcv_handoff


EQUITIES_CSV = Path("tests/fixtures/vendor_flat_files/polygon/equities/daily/2026/01/15/equities_daily_2026-01-15_sample.csv")
EQUITIES_MANIFEST = Path("tests/fixtures/vendor_flat_files/polygon/equities/daily/2026/01/15/manifest.json")
ETFS_CSV = Path("tests/fixtures/vendor_flat_files/polygon/etfs/daily/2026/01/15/etfs_daily_2026-01-15_sample.csv")
ETFS_MANIFEST = Path("tests/fixtures/vendor_flat_files/polygon/etfs/daily/2026/01/15/manifest.json")


def _equities_parsed():
    return parse_local_ohlcv_fixture(EQUITIES_CSV, EQUITIES_MANIFEST, expected_asset_class="equities", expected_observation_date="2026-01-15")


def _etfs_parsed():
    return parse_local_ohlcv_fixture(ETFS_CSV, ETFS_MANIFEST, expected_asset_class="etfs", expected_observation_date="2026-01-15")


def test_builds_canonical_records_from_parsed_equities_fixture_result() -> None:
    parsed = _equities_parsed()
    result = build_ohlcv_handoff(parsed)

    assert result.handoff_status == "BLOCKED"
    assert result.record_count == 3
    assert result.symbols == ("AAPL", "MSFT", "NVDA")
    assert result.records[0]["canonical_schema_version"] == "canonical_ohlcv.v1"
    assert result.records[0]["evidence_type"] == "vendor_flat_file_ohlcv"
    assert result.records[0]["manifest_path"].endswith("manifest.json")
    assert result.records[0]["lineage_id"] == "fixture-lineage-equities-2026-01-15"
    assert result.records[0]["source_file_sha256"] == parsed.source_file_sha256
    assert result.records[0]["trade_date"] == result.records[0]["observation_date"]
    assert result.records[0]["source_vendor"] == result.records[0]["vendor"]
    assert result.records[0]["adjustment_status"] in {"adjusted", "unadjusted"}


def test_builds_canonical_records_from_parsed_etf_fixture_result() -> None:
    parsed = _etfs_parsed()
    result = build_ohlcv_handoff(parsed)

    assert result.handoff_status == "BLOCKED"
    assert result.record_count == 5
    assert result.records[0]["canonical_schema_version"] == "canonical_ohlcv.v1"
    assert result.records[0]["evidence_type"] == "vendor_flat_file_ohlcv"


def test_idempotency_key_deterministic_across_repeated_calls() -> None:
    parsed = _equities_parsed()
    first = build_ohlcv_handoff(parsed)
    second = build_ohlcv_handoff(parsed)

    assert first.records[0]["idempotency_key"] == second.records[0]["idempotency_key"]
    assert first.idempotency_key_prefixes == second.idempotency_key_prefixes


def test_missing_adjustment_status_defaults_to_unknown_or_vendor_default() -> None:
    parsed = _equities_parsed()
    mutated_rows = []
    for row in parsed.rows:
        updated = dict(row)
        updated.pop("adjusted", None)
        updated.pop("adjustment_status", None)
        updated.pop("adjusted_status", None)
        mutated_rows.append(updated)
    mutated = type(parsed)(
        parse_status=parsed.parse_status,
        rows=tuple(mutated_rows),
        row_count=parsed.row_count,
        symbols=parsed.symbols,
        warnings=parsed.warnings,
        errors=parsed.errors,
        manifest=parsed.manifest,
        source_file_sha256=parsed.source_file_sha256,
    )
    result = build_ohlcv_handoff(mutated)
    assert result.records[0]["adjusted"] is False
    assert result.records[0]["adjustment_status"] == "unknown_or_vendor_default"


def test_idempotency_key_changes_when_source_file_sha_changes() -> None:
    parsed = _equities_parsed()
    mutated_rows = []
    for row in parsed.rows:
        updated = dict(row)
        updated["source_file_sha256"] = "f" * 64
        mutated_rows.append(updated)
    mutated = type(parsed)(
        parse_status=parsed.parse_status,
        rows=tuple(mutated_rows),
        row_count=parsed.row_count,
        symbols=parsed.symbols,
        warnings=parsed.warnings,
        errors=parsed.errors,
        manifest=parsed.manifest,
        source_file_sha256="f" * 64,
    )
    first = build_ohlcv_handoff(parsed)
    second = build_ohlcv_handoff(mutated)
    assert first.records[0]["idempotency_key"] != second.records[0]["idempotency_key"]


def test_safe_summary_exposes_prefix_only() -> None:
    result = build_ohlcv_handoff(_equities_parsed())
    assert result.safe_summary is not None
    assert "idempotency_key_prefixes" in result.safe_summary
    full_keys = [record["idempotency_key"] for record in result.records]
    summary_text = json.dumps(result.safe_summary)
    assert all(full_key not in summary_text for full_key in full_keys)


def test_fixture_only_blocks_handoff_with_blocked_error() -> None:
    result = build_ohlcv_handoff(_equities_parsed())
    assert result.handoff_status == "BLOCKED"
    assert any(error.code == "HANDOFF_BLOCKED_FIXTURE_ONLY" for error in result.errors)


def test_validation_failure_blocks_handoff() -> None:
    parsed = _equities_parsed()
    bad = type(parsed)(
        parse_status="FAIL",
        rows=parsed.rows,
        row_count=parsed.row_count,
        symbols=parsed.symbols,
        warnings=parsed.warnings,
        errors=parsed.errors + tuple([parsed.errors[0]] if parsed.errors else []),
        manifest=parsed.manifest,
        source_file_sha256=parsed.source_file_sha256,
    )
    result = build_ohlcv_handoff(bad)
    assert result.handoff_status in {"BLOCKED", "FAIL"}
    assert any(error.code == "HANDOFF_BLOCKED_VALIDATION_FAILED" for error in result.errors)


def test_missing_checksum_blocks_handoff() -> None:
    parsed = _equities_parsed()
    mutated_rows = [dict(row) for row in parsed.rows]
    for row in mutated_rows:
        row["source_file_sha256"] = ""
    mutated = type(parsed)(
        parse_status=parsed.parse_status,
        rows=tuple(mutated_rows),
        row_count=parsed.row_count,
        symbols=parsed.symbols,
        warnings=parsed.warnings,
        errors=parsed.errors,
        manifest={**(parsed.manifest or {}), "source_file_sha256": ""},
        source_file_sha256="",
    )
    result = build_ohlcv_handoff(mutated)
    assert any(error.code == "HANDOFF_BLOCKED_CHECKSUM_MISSING" for error in result.errors)


def test_missing_certification_blocks_handoff() -> None:
    parsed = _equities_parsed()
    manifest = dict(parsed.manifest or {})
    manifest["certification_status"] = ""
    mutated = type(parsed)(
        parse_status=parsed.parse_status,
        rows=parsed.rows,
        row_count=parsed.row_count,
        symbols=parsed.symbols,
        warnings=parsed.warnings,
        errors=parsed.errors,
        manifest=manifest,
        source_file_sha256=parsed.source_file_sha256,
    )
    result = build_ohlcv_handoff(mutated)
    assert any(error.code == "HANDOFF_BLOCKED_CERTIFICATION_MISSING" for error in result.errors)


def test_output_preserves_manifest_lineage_and_checksum() -> None:
    result = build_ohlcv_handoff(_equities_parsed())
    assert result.records[0]["manifest_path"].endswith("manifest.json")
    assert result.records[0]["lineage_id"] == "fixture-lineage-equities-2026-01-15"
    assert result.records[0]["source_file_sha256"] == hashlib.sha256(EQUITIES_CSV.read_bytes()).hexdigest()


def test_no_env_vars_read_no_db_writer_no_requests_imports() -> None:
    with patch("os.getenv") as getenv_mock:
        result = build_ohlcv_handoff(_equities_parsed())
    assert getenv_mock.call_count == 0
    assert result.records
    source = Path("app/vendor_flat_files/ohlcv_handoff_builder.py").read_text(encoding="utf-8").lower()
    for marker in ["requests", "httpx", "sqlalchemy", "writer", "session", "database", "vendor sdk"]:
        assert marker not in source


def test_no_output_files_written() -> None:
    before = set(Path(".").glob("**/handoff_builder_output*"))
    build_ohlcv_handoff(_equities_parsed())
    after = set(Path(".").glob("**/handoff_builder_output*"))
    assert before == after


def test_no_production_evidence_generated() -> None:
    result = build_ohlcv_handoff(_equities_parsed())
    assert result.safe_summary is not None
    assert result.safe_summary["not_production_evidence"] is True
    assert result.records[0]["certification_status"] == "FIXTURE_ONLY"
