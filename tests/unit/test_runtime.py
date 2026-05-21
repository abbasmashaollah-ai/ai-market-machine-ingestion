import unittest

from app.core.runtime import generate_run_id


class RuntimeTests(unittest.TestCase):
    def test_generate_run_id_is_hex_string(self) -> None:
        run_id = generate_run_id()
        self.assertEqual(len(run_id), 32)
        int(run_id, 16)
