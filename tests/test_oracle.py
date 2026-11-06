# -*- coding: utf-8 -*-
"""Design oracle: closed-form refer resolution."""
from __future__ import annotations

import unittest

from deckforge.core.deck import render_deck
from deckforge.world.oracle import DesignWorld


class TestOracle(unittest.TestCase):
    def setUp(self):
        self.world = DesignWorld()
        self.deck = render_deck(seed="x", template="pitch")

    def test_refer_by_label(self):
        self.assertEqual(self.world.refer_to_element(self.deck, "headline"),
                         "title")

    def test_refer_by_eid(self):
        self.assertEqual(self.world.refer_to_element(self.deck, "title"), "title")

    def test_expected_spec(self):
        outline = {"id": "d00", "template": "pitch",
                   "points": [("title", "headline"), ("footer", "footer")]}
        spec = self.world.expected_spec(outline, self.deck)
        self.assertEqual(spec[0], ("title", "title"))
        self.assertEqual(spec[1], ("footer", "footer"))


if __name__ == "__main__":
    unittest.main()
