from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.core.health import check_runtime_health
from scripts.railway_start import main as railway_start_main


class RailwayDeploymentTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_healthcheck_does_not_require_database_url(self) -> None:
        os.environ.pop("DATABASE_URL", None)

        status = check_runtime_health()

        self.assertTrue(status.app_imports_ok)
        self.assertTrue(status.config_shape_ok)
        self.assertFalse(status.database_url_present)
        self.assertIsNone(status.database_url_valid)
        self.assertTrue(status.ok)

    def test_healthcheck_does_not_call_vendors_or_db(self) -> None:
        os.environ.pop("DATABASE_URL", None)

        with patch("app.core.config.load_settings", side_effect=AssertionError("load_settings should not run")) as load_settings_mock:
            with patch("app.core.health.urlparse") as urlparse_mock:
                status = check_runtime_health()

        load_settings_mock.assert_not_called()
        urlparse_mock.assert_not_called()
        self.assertTrue(status.ok)

    def test_healthcheck_flags_invalid_database_url_without_connecting(self) -> None:
        os.environ["DATABASE_URL"] = "not-a-url"

        with patch("app.core.health.urlparse") as urlparse_mock:
            urlparse_mock.return_value = type("Parsed", (), {"scheme": "", "netloc": ""})()
            status = check_runtime_health()

        urlparse_mock.assert_called_once()
        self.assertFalse(status.ok)
        self.assertFalse(status.database_url_valid)

    def test_railway_start_is_safe_and_idle(self) -> None:
        os.environ.pop("DATABASE_URL", None)

        with patch("builtins.print") as print_mock:
            exit_code = railway_start_main()

        self.assertEqual(exit_code, 0)
        self.assertGreaterEqual(print_mock.call_count, 2)
