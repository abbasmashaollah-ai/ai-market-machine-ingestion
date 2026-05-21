import unittest

from app.models.vendor import VendorPayloadMetadata


class VendorPayloadMetadataTests(unittest.TestCase):
    def test_vendor_payload_metadata_shape(self) -> None:
        metadata = VendorPayloadMetadata(
            vendor="polygon",
            source="equities",
            request_id="req-1",
            correlation_id="corr-1",
            content_type="application/json",
            payload_version="v1",
        )

        self.assertEqual(metadata.vendor, "polygon")
        self.assertEqual(metadata.source, "equities")
        self.assertEqual(metadata.request_id, "req-1")
        self.assertEqual(metadata.content_type, "application/json")
