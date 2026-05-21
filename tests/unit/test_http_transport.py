import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from app.vendors.common.errors import VendorHttpStatusError, VendorTimeoutError, VendorUnavailableError
from app.vendors.common.http import HttpResponse, RequestMetadata, UrlLibHttpClient, build_request_metadata


class HttpTransportTests(unittest.TestCase):
    def test_successful_json_response(self) -> None:
        response = Mock()
        response.read.return_value = b'{"ok": true}'
        response.status = 200
        response.headers = {"Content-Type": "application/json"}
        client = UrlLibHttpClient()

        with patch("app.vendors.common.http.request.urlopen", return_value=response):
            result = client.request(build_request_metadata("https://example.com", timeout_seconds=5.0))

        self.assertIsInstance(result, HttpResponse)
        self.assertEqual(result.json, {"ok": True})
        self.assertEqual(result.metadata.status_code, 200)

    def test_non_json_text_response(self) -> None:
        response = Mock()
        response.read.return_value = b"plain text"
        response.status = 200
        response.headers = {}
        client = UrlLibHttpClient()

        with patch("app.vendors.common.http.request.urlopen", return_value=response):
            result = client.request(build_request_metadata("https://example.com", timeout_seconds=5.0))

        self.assertEqual(result.text, "plain text")
        self.assertIsNone(result.json)

    def test_timeout_mapping(self) -> None:
        client = UrlLibHttpClient()
        with patch("app.vendors.common.http.request.urlopen", side_effect=TimeoutError("timeout")):
            with self.assertRaises(VendorTimeoutError):
                client.request(build_request_metadata("https://example.com", timeout_seconds=1.0))

    def test_http_error_status_mapping(self) -> None:
        client = UrlLibHttpClient()
        with patch(
            "app.vendors.common.http.request.urlopen",
            side_effect=HTTPError("https://example.com", 500, "server error", hdrs=None, fp=None),
        ):
            with self.assertRaises(VendorHttpStatusError):
                client.request(build_request_metadata("https://example.com", timeout_seconds=1.0))

    def test_query_param_handling(self) -> None:
        response = Mock()
        response.read.return_value = b"{}"
        response.status = 200
        response.headers = {}
        client = UrlLibHttpClient()

        with patch("app.vendors.common.http.request.urlopen", return_value=response) as mocked:
            client.request(
                build_request_metadata(
                    "https://example.com/path",
                    timeout_seconds=5.0,
                    query_params={"a": "1", "b": "2"},
                )
            )

        called_request = mocked.call_args[0][0]
        self.assertIn("a=1", called_request.full_url)
        self.assertIn("b=2", called_request.full_url)

    def test_no_live_network_calls(self) -> None:
        client = UrlLibHttpClient()
        with patch("app.vendors.common.http.request.urlopen", side_effect=VendorUnavailableError("blocked")):
            with self.assertRaises(VendorUnavailableError):
                client.request(build_request_metadata("https://example.com", timeout_seconds=1.0))
