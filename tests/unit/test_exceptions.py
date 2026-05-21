import unittest

from app.core.exceptions import CheckpointError, ConfigError, ValidationError, VendorError, WriterError


class ExceptionImportTests(unittest.TestCase):
    def test_exception_classes_import(self) -> None:
        self.assertTrue(issubclass(ConfigError, Exception))
        self.assertTrue(issubclass(VendorError, Exception))
        self.assertTrue(issubclass(ValidationError, Exception))
        self.assertTrue(issubclass(WriterError, Exception))
        self.assertTrue(issubclass(CheckpointError, Exception))
