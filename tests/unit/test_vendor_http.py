import unittest

from app.vendors.common.http import RequestMetadata, ResponseMetadata


class VendorHttpMetadataTests(unittest.TestCase):
    def test_request_metadata_shape(self) -> None:
        request = RequestMetadata(method="GET", url="https://example.com", timeout_seconds=5.0)
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.url, "https://example.com")
        self.assertEqual(request.timeout_seconds, 5.0)
        self.assertEqual(request.headers, {})

    def test_response_metadata_shape(self) -> None:
        response = ResponseMetadata(status_code=200, elapsed_seconds=0.25)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.elapsed_seconds, 0.25)
        self.assertEqual(response.headers, {})
