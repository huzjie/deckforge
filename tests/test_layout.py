# -*- coding: utf-8 -*-
"""Layout stage: element placement + bbox hit."""
from __future__ import annotations

import unittest

from deckforge.core.deck import render_deck
from deckforge.core.layout import Layouter
from deckforge.kit import build_kit
from deckforge.config import load_config


class TestLayout(unittest.TestCase):
    def setUp(self):
        self.kit = build_kit(load_config())
        self.layouter = Layouter(self.kit["cfg"]["model"]["dim"])

    def test_oracle_locate_hits(self):
        deck = self.kit["corpus"]["templates"]["pitch"]
        target = deck.by_label("headline")
        eid, (x, y) = self.layouter.locate(deck, "headline", 1.0, target.eid)
        self.assertEqual(eid, target.eid)
        self.assertTrue(target.contains(x, y))

    def test_baseline_may_miss(self):
        deck = self.kit["corpus"]["templates"]["pitch"]
        target = deck.by_label("headline")
        eid, (x, y), hit = self.layouter.hit(deck, "headline", 0.0, target.eid)
        self.assertIsInstance(eid, str)
        self.assertIsInstance(hit, bool)


if __name__ == "__main__":
    unittest.main()
