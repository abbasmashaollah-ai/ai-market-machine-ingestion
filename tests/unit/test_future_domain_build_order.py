from __future__ import annotations

import unittest
from pathlib import Path


class FutureDomainBuildOrderTests(unittest.TestCase):
    def test_build_order_doc_exists_and_is_ordered(self) -> None:
        text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
        expected_order = [
            "symbol master",
            "etf/index universe expansion",
            "polygon flat-file ohlcv",
            "fred macro",
            "volatility indexes",
            "event calendars/earnings",
            "fundamentals",
            "news",
            "cross-asset ohlcv",
            "breadth/participation",
            "options",
            "flows/positioning",
        ]
        position = -1
        for item in expected_order:
            new_position = text.find(item)
            self.assertGreater(new_position, position)
            position = new_position
