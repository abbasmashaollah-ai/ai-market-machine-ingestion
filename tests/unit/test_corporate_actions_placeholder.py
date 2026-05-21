import unittest

from app.normalization.corporate_actions import CorporateActionPayload, normalize_corporate_actions


class CorporateActionPlaceholderTests(unittest.TestCase):
    def test_placeholder_structure(self) -> None:
        payload = CorporateActionPayload(raw={"example": True})
        self.assertEqual(payload.raw["example"], True)

    def test_not_implemented_boundary(self) -> None:
        with self.assertRaises(NotImplementedError):
            normalize_corporate_actions({})
