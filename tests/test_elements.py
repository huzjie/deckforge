# -*- coding: utf-8 -*-
"""Element vocabulary + layout-zone validity."""
from __future__ import annotations

import unittest

from deckforge.core.elements import LAYOUT_ZONE, validate_element, count_conflicts
from deckforge.core.deck import render_deck


class TestElements(unittest.TestCase):
    def test_validate_in_zone(self):
        self.assertTrue(validate_element("title", (0.05, 0.05, 0.9, 0.14)))
        self.assertTrue(validate_element("footer", (0.05, 0.88, 0.9, 0.93)))
        self.assertTrue(validate_element("bullet", (0.07, 0.40, 0.45, 0.55)))

    def test_validate_out_of_zone(self):
        self.assertFalse(validate_element("title", (0.05, 0.50, 0.9, 0.60)))
        self.assertFalse(validate_element("footer", (0.05, 0.10, 0.9, 0.20)))

    def test_canonical_deck_no_conflicts(self):
        deck = render_deck(seed="x", template="report")
        self.assertEqual(count_conflicts(deck.elements), 0)


if __name__ == "__main__":
    unittest.main()
