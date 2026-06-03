from unittest.mock import Mock

import pytest

from app.clients.data_read_client import (
    DataReadClient,
    DataReadClientAuthError,
    DataReadClientConfig,
    DataReadClientResponseError,
    DataReadClientTimeoutError,
)
from app.vendors.common.http import HttpResponse, ResponseMetadata


def _response(status_code: int, payload: object) -> HttpResponse:
    return HttpResponse(
        metadata=ResponseMetadata(status_code=status_code, elapsed_seconds=0.01),
        text="{}",
        json=payload,
    )


def test_config_strips_trailing_slash() -> None:
    config = DataReadClientConfig(base_url="https://example.com/", ops_internal_token="secret")
    assert config.base_url == "https://example.com"


def test_missing_base_url_rejected() -> None:
    with pytest.raises(ValueError, match="base_url is required"):
        DataReadClientConfig(base_url=" ", ops_internal_token="secret")


def test_missing_token_rejected() -> None:
    with pytest.raises(ValueError, match="ops_internal_token is required"):
        DataReadClientConfig(base_url="https://example.com", ops_internal_token=" ")


def test_request_includes_internal_token_and_params() -> None:
    transport = Mock()
    transport.request.return_value = _response(200, [{"symbol": "SPY", "close": 100.0}])
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com/", ops_internal_token="secret"), http_client=transport)

    result = client.get_certified_ohlcv_history(["spy", "xlk"], start_date="2026-01-01", end_date="2026-01-31", lookback_days=61)

    metadata = transport.request.call_args[0][0]
    assert metadata.method == "GET"
    assert metadata.url == "https://example.com/private-read/canonical_ohlcv/certified-history"
    assert metadata.headers["X-Ops-Internal-Token"] == "secret"
    assert metadata.query_params["symbols"] == "SPY,XLK"
    assert metadata.query_params["start_date"] == "2026-01-01"
    assert metadata.query_params["end_date"] == "2026-01-31"
    assert metadata.query_params["lookback_days"] == "61"
    assert result == [{"symbol": "SPY", "close": 100.0}]


def test_token_not_exposed_in_repr_or_errors() -> None:
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"))
    text = repr(client)
    assert "secret" not in text

    transport = Mock()
    transport.request.return_value = _response(401, {"error": "unauthorized"})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    with pytest.raises(DataReadClientAuthError) as ctx:
        client.get_certified_ohlcv_history(["SPY"])

    assert "secret" not in str(ctx.value)


def test_successful_response_returns_rows() -> None:
    transport = Mock()
    transport.request.return_value = _response(200, {"rows": [{"symbol": "SPY", "close": 100.0}]})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    result = client.get_certified_ohlcv_history(["SPY"])
    assert result == [{"symbol": "SPY", "close": 100.0}]


def test_auth_failure_raises_auth_error() -> None:
    transport = Mock()
    transport.request.return_value = _response(403, {"error": "forbidden"})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    with pytest.raises(DataReadClientAuthError):
        client.get_certified_ohlcv_history(["SPY"])


def test_server_failure_raises_response_error() -> None:
    transport = Mock()
    transport.request.return_value = _response(500, {"error": "server error"})
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    with pytest.raises(DataReadClientResponseError):
        client.get_certified_ohlcv_history(["SPY"])


def test_timeout_raises_timeout_error() -> None:
    transport = Mock()
    transport.request.side_effect = DataReadClientTimeoutError("timed out")
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)

    with pytest.raises(DataReadClientTimeoutError):
        client.get_certified_ohlcv_history(["SPY"])


def test_no_post_put_patch_delete_behavior_exists() -> None:
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"))
    methods = {name for name in dir(client) if name.lower() in {"post", "put", "patch", "delete"}}
    assert methods == set()


def test_no_vendor_fallback_by_construction() -> None:
    transport = Mock()
    transport.request.return_value = _response(200, [{"symbol": "SPY", "close": 100.0}])
    client = DataReadClient(DataReadClientConfig(base_url="https://example.com", ops_internal_token="secret"), http_client=transport)
    client.get_certified_ohlcv_history(["SPY"])
    assert transport.request.call_count == 1

