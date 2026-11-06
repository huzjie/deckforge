# -*- coding: utf-8 -*-
"""Design stage: outline -> element spec."""
from __future__ import annotations

import unittest

from deckforge.core.designer import Designer
from deckforge.kit import build_kit
from deckforge.config import load_config


class TestDesigner(unittest.TestCase):
    def setUp(self):
        self.kit = build_kit(load_config())
        self.designer = Designer(self.kit["world"])

    def test_oracle_design_matches(self):
        outline = self.kit["corpus"]["decks"][0]
        deck = self.kit["corpus"]["templates"][outline["template"]]
        spec = self.designer.design(outline, deck, 1.0)
        expected = self.kit["world"].expected_spec(outline, deck)
        self.assertEqual(spec, expected)

    def test_baseline_design_length(self):
        outline = self.kit["corpus"]["decks"][0]
        deck = self.kit["corpus"]["templates"][outline["template"]]
        spec = self.designer.design(outline, deck, 0.0)
        self.assertEqual(len(spec), len(outline["points"]))


if __name__ == "__main__":
    unittest.main()
