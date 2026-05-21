import unittest

from app.vendors.common.errors import (
    InvalidVendorResponseError,
    VendorRateLimitedError,
    VendorTimeoutError,
    VendorUnavailableError,
)


class VendorErrorTests(unittest.TestCase):
    def test_vendor_exceptions_import(self) -> None:
        self.assertTrue(issubclass(VendorUnavailableError, Exception))
        self.assertTrue(issubclass(VendorRateLimitedError, Exception))
        self.assertTrue(issubclass(VendorTimeoutError, Exception))
        self.assertTrue(issubclass(InvalidVendorResponseError, Exception))
