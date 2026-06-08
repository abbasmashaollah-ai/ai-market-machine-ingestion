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


class _FakeDownloadClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def download_file(self, **kwargs: object) -> None:
        self.calls.append(kwargs)
        path = Path(str(kwargs["Filename"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake gzip bytes")

    def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        prefix = str(kwargs.get("Prefix") or "")
        if prefix.endswith("us_stocks_sip/day_aggs_v1/2003/09"):
            return {
                "Contents": [
                    {
                        "Key": "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz",
                        "Size": 17,
                        "LastModified": "x",
                        "ETag": "etag-1",
                    }
                ]
            }
        return {"Contents": []}

    class _Body:
        def __init__(self, payload: bytes) -> None:
            self._payload = payload
            self._offset = 0

        def read(self, size: int) -> bytes:
            if self._offset >= len(self._payload):
                return b""
            chunk = self._payload[self._offset : self._offset + size]
            self._offset += len(chunk)
            return chunk

    def get_object(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        if kwargs.get("Key") == "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz":
            payload = b"fake gzip bytes"
            return {"Body": self._Body(payload), "ContentLength": len(payload)}
        raise RuntimeError("unexpected key")


class _DownloadableAdapter(PolygonFlatFileAdapter):
    @staticmethod
    def boto3_available() -> bool:
        return True


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


def test_date_range_and_manifest_tail_pattern_are_csv_gzip_based() -> None:
    assert PolygonFlatFileAdapter._date_range("2003-09-10", "2003-09-10", 25)[0].isoformat() == "2003-09-10"
    assert PolygonFlatFileAdapter._date_range("2026-01-02", "2026-01-02", 25)[0].isoformat() == "2026-01-02"
    assert PolygonFlatFileAdapter.redacted_csv_gzip_tail("2003-09-10") == "09/2003-09-10.csv.gz"
    assert PolygonFlatFileAdapter.redacted_csv_gzip_tail("2026-01-02") == "01/2026-01-02.csv.gz"
    assert f"us_stocks_sip/day_aggs_v1/{PolygonFlatFileAdapter._normalize_date('2003-09-10'):%Y/%m}" == "us_stocks_sip/day_aggs_v1/2003/09"
    assert f"us_stocks_sip/day_aggs_v1/{PolygonFlatFileAdapter._normalize_date('2026-01-02'):%Y/%m}" == "us_stocks_sip/day_aggs_v1/2026/01"
    assert PolygonFlatFileAdapter.redacted_csv_gzip_tail("us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz") == "09/2003-09-10.csv.gz"
    assert PolygonFlatFileAdapter.redacted_csv_gzip_tail("us_stocks_sip/day_aggs_v1/2026/01/2026-01-02.csv.gz") == "01/2026-01-02.csv.gz"
    assert PolygonFlatFileAdapter.stock_day_aggs_object_key("2003-09-10") == "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz"
    assert PolygonFlatFileAdapter.stock_day_aggs_object_key("2026-01-02") == "us_stocks_sip/day_aggs_v1/2026/01/2026-01-02.csv.gz"
    assert PolygonFlatFileAdapter.sha256_prefix("us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz") == PolygonFlatFileAdapter.sha256_prefix("us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz")


def test_download_single_date_object_writes_local_file_and_sha256(monkeypatch, tmp_path) -> None:
    adapter = _DownloadableAdapter(
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )
    fake = _FakeDownloadClient()
    monkeypatch.setattr(adapter, "build_remote_listing_client", lambda: fake)
    local_path = tmp_path / "polygon_stocks_day_aggs_2003-09-10.csv.gz"
    result = adapter.download_single_date_object(value="2003-09-10", local_path=local_path)
    assert result["downloaded"] is True
    assert result["local_file_exists"] is True
    assert result["local_file_size_bytes"] > 0
    assert result["local_file_sha256"]
    assert result["redacted_key_tail"] == "09/2003-09-10.csv.gz"
    assert result["content_length_present"] is True
    assert result["resolved_key_present"] is True
    assert result["resolved_key_tail_matches_requested_date"] is True
    assert result["resolved_key_sha256_prefix"] == result["listed_key_sha256_prefix"]
    assert result["resolved_key_matches_listed_key"] is True
    assert any(call.get("Key") == "us_stocks_sip/day_aggs_v1/2003/09/2003-09-10.csv.gz" for call in fake.calls)
    assert any("get_object" not in call for call in fake.calls if isinstance(call, dict))


def test_download_single_date_object_skips_when_manifest_missing(monkeypatch, tmp_path) -> None:
    adapter = _DownloadableAdapter(
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )

    class _MissingClient(_FakeDownloadClient):
        def list_objects_v2(self, **kwargs: object) -> dict[str, object]:
            self.calls.append(kwargs)
            return {"Contents": []}

    fake = _MissingClient()
    monkeypatch.setattr(adapter, "build_remote_listing_client", lambda: fake)
    local_path = tmp_path / "polygon_stocks_day_aggs_2003-09-10.csv.gz"
    result = adapter.download_single_date_object(value="2003-09-10", local_path=local_path)
    assert result["downloaded"] is False
    assert result["local_file_exists"] is False
    assert result["resolved_key_present"] is False
    assert result["resolved_key_sha256_prefix"] == ""
    assert len(fake.calls) == 1
    assert "Key" not in fake.calls[0]


def test_download_single_date_object_uses_get_object_stream_and_forbidden_maps_safely(monkeypatch, tmp_path) -> None:
    adapter = _DownloadableAdapter(
        {
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID": "polygon-key",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY": "polygon-secret",
            "POLYGON_FLAT_FILE_ENDPOINT": "https://endpoint.invalid",
            "POLYGON_FLAT_FILE_BUCKET": "bucket",
            "POLYGON_FLAT_FILE_PREFIX": "prefix",
        }
    )

    class _ForbiddenClient(_FakeDownloadClient):
        def get_object(self, **kwargs: object) -> dict[str, object]:
            raise _FakeClientError({"Error": {"Code": "AccessDenied", "Message": "Forbidden"}, "ResponseMetadata": {"HTTPStatusCode": 403}})

    fake = _ForbiddenClient()
    monkeypatch.setattr(adapter, "build_remote_listing_client", lambda: fake)
    local_path = tmp_path / "polygon_stocks_day_aggs_2003-09-10.csv.gz"
    result = adapter.download_single_date_object(value="2003-09-10", local_path=local_path)
    assert result["downloaded"] is False
    assert result["remote_download_status"] == "forbidden"
    assert result["resolved_key_present"] is True
    assert result["resolved_key_tail_matches_requested_date"] is True
    assert result["resolved_key_matches_listed_key"] is True
    assert not local_path.exists()
