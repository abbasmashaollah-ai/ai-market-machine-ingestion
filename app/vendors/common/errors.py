from __future__ import annotations


class VendorError(Exception):
    """Base class for vendor-related failures."""


class VendorUnavailableError(VendorError):
    """Raised when a vendor cannot be reached or is offline."""


class VendorRateLimitedError(VendorError):
    """Raised when a vendor rate limit has been exceeded."""


class VendorTimeoutError(VendorError):
    """Raised when a vendor request times out."""


class InvalidVendorResponseError(VendorError):
    """Raised when a vendor response cannot be parsed or validated."""
