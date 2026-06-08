from __future__ import annotations

import json
from pathlib import Path

import pytest
from dataclasses import asdict

from app.vendor_flat_files.polygon_flat_file_adapter import (
    BENCHMARK_SYMBOL,
    EXPECTED_FLAT_FILE_DATASET_TYPE,
    PolygonFlatFileAdapter,
    REQUIRED_CONFIG_NAMES,
    SECTOR_ETF_UNIVERSE,
    SECTOR_SYMBOLS,
    benchmark_symbol,
    detect_config_presence,
    expected_flat_file_dataset_type,
    required_config_names,
    sector_etf_symbols,
    sector_etf_universe_symbols,
    summarize_capability,
)


class _FakeClientError(Exception):
    def __init__(self, response: dict[str, object]) -> None:
        super().__init__("client error")
        self.response = response


def test_required_config_names_and_universe_are_name_only() -> None:
    assert required_config_names() == REQUIRED_CONFIG_NAMES
    assert sector_etf_symbols() == SECTOR_SYMBOLS
    assert sector_etf_universe_symbols() == SECTOR_ETF_UNIVERSE
    assert benchmark_symbol() == BENCHMARK_SYMBOL
    assert expected_flat_file_dataset_type() == EXPECTED_FLAT_FILE_DATASET_TYPE


def test_config_presence_and_safe_summary_do_not_expose_values(monkeypatch) -> None:
    monkeypatch.setenv("POLYGON_API_KEY", "polygon-secret")
    monkeypatch.setenv("POLYGON_FLAT_FILE_BUCKET", "redacted-bucket")
    env = {
        "POLYGON_API_KEY": "polygon-secret",
        "POLYGON_FLAT_FILE_BUCKET": "redacted-bucket",
    }
    presence = detect_config_presence(env)
    assert presence["credentials_present"] is True
    assert "POLYGON_API_KEY" in presence["present_config_names"]
    summary = summarize_capability(
        env=env,
        local_parser_detected=True,
        handoff_builder_detected=True,
    )
    payload = json.loads(json.dumps(asdict(summary)))
    assert payload["credentials_printed"] is False
    text = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["polygon-secret", "redacted-bucket", "postgresql", "http://", "https://"]:
        assert forbidden not in text


def test_adapter_stub_methods_are_not_implemented() -> None:
    adapter = PolygonFlatFileAdapter(env={})
    with pytest.raises(NotImplementedError):
        adapter.list_remote_flat_files()
    with pytest.raises(NotImplementedError):
        adapter.download_flat_file()
    with pytest.raises(NotImplementedError):
        adapter.build_manifest()
    with pytest.raises(NotImplementedError):
        adapter.build_production_handoff()


def test_safe_summary_includes_expected_sector_universe() -> None:
    adapter = PolygonFlatFileAdapter(env={})
    payload = adapter.safe_summary()
    assert payload["benchmark_symbol"] == "SPY"
    assert payload["required_sector_symbols"] == ["XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"]
    assert payload["production_eligible_generation_authorized"] is False
    assert payload["synthetic_forbidden"] is True
    assert payload["fixture_only_forbidden"] is True
    assert payload["credentials_printed"] is False


def test_no_network_or_db_imports_in_adapter_source() -> None:
    source = Path("app/vendor_flat_files/polygon_flat_file_adapter.py").read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "requests",
        "httpx",
        "sqlalchemy",
        "create_engine",
        "session",
        "database_url",
        "ingest",
        "scheduler",
        "download(",
        "export(",
    ]
    for term in forbidden_terms:
        assert term not in source


def test_adapter_exposes_boto3_gate_and_remote_listing_helpers() -> None:
    adapter = PolygonFlatFileAdapter(env={})
    assert isinstance(adapter.boto3_available(), bool)
    assert hasattr(adapter, "build_remote_listing_client")
    assert hasattr(adapter, "list_remote_objects")


def test_adapter_classifies_client_error_403_safely() -> None:
    error = _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})
    code, redacted_code, message = PolygonFlatFileAdapter.classify_remote_listing_error(error)
    assert code == "forbidden"
    assert redacted_code == "forbidden"
    assert message == "remote listing failed safely"
