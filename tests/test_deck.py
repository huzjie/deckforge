# -*- coding: utf-8 -*-
"""Deterministic deck rendering."""
from __future__ import annotations

import unittest

from deckforge.core.deck import render_deck, TEMPLATES, ELEMENT_TYPES


class TestDeck(unittest.TestCase):
    def test_render_deterministic(self):
        a = render_deck(seed="x", template="pitch", grid_w=40, grid_h=24)
        b = render_deck(seed="x", template="pitch", grid_w=40, grid_h=24)
        self.assertEqual(a.grid, b.grid)
        self.assertEqual([e.bbox for e in a.elements], [e.bbox for e in b.elements])

    def test_elements_in_template(self):
        deck = render_deck(seed="x", template="report")
        self.assertEqual(len(deck.elements), len(TEMPLATES["report"]))

    def test_grid_shape(self):
        deck = render_deck(seed="x", template="tutorial", grid_w=40, grid_h=24)
        self.assertEqual(len(deck.grid), 24)
        self.assertTrue(all(len(row) == 40 for row in deck.grid))

    def test_by_label(self):
        deck = render_deck(seed="x", template="pitch")
        self.assertIsNotNone(deck.by_label("headline"))
        self.assertIsNone(deck.by_label("nonexistent"))

    def test_element_contains(self):
        deck = render_deck(seed="x", template="pitch")
        el = deck.by_label("headline")
        cx, cy = el.center
        self.assertTrue(el.contains(cx, cy))


if __name__ == "__main__":
    unittest.main()
