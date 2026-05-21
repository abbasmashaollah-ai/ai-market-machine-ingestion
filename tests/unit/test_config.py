import os
import unittest

from app.core.config import ConfigError, load_settings


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_load_settings_from_environment(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example"
        os.environ["INGESTION_BATCH_SIZE"] = "250"
        os.environ["INGESTION_MAX_RETRIES"] = "5"
        os.environ["BACKFILL_START_DATE"] = "2026-01-01"

        settings = load_settings()

        self.assertEqual(settings.DATABASE_URL, "postgresql://example")
        self.assertEqual(settings.INGESTION_BATCH_SIZE, 250)
        self.assertEqual(settings.INGESTION_MAX_RETRIES, 5)
        self.assertEqual(str(settings.BACKFILL_START_DATE), "2026-01-01")

    def test_missing_database_url_raises(self) -> None:
        os.environ.pop("DATABASE_URL", None)

        with self.assertRaises(ConfigError):
            load_settings()
