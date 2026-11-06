# -*- coding: utf-8 -*-
"""Semantic encoder: deterministic embeddings + outline alignment."""
from __future__ import annotations

import unittest

from deckforge.core.deck import render_deck
from deckforge.core.embed import (encode_deck, encode_element, refer_embedding,
                                  cosine_match)
from deckforge.utils.linalg import cosine


class TestEmbed(unittest.TestCase):
    def setUp(self):
        self.deck = render_deck(seed="x", template="pitch")
        self.dim = 16

    def test_encode_deck(self):
        scene, vecs = encode_deck(self.deck, self.dim)
        self.assertEqual(len(scene), self.dim)
        self.assertEqual(len(vecs), len(self.deck.elements))

    def test_cosine_match_picks_self(self):
        _, vecs = encode_deck(self.deck, self.dim)
        el = self.deck.elements[0]
        ideal = encode_element(el, self.dim)
        self.assertEqual(cosine_match(vecs, ideal), el.eid)

    def test_refer_embedding_skill_blend(self):
        el = self.deck.elements[0]
        ideal = encode_element(el, self.dim)
        full = refer_embedding(el.label, ideal, 1.0, self.dim)
        self.assertAlmostEqual(cosine(full, ideal), 1.0, places=6)
        zero = refer_embedding(el.label, ideal, 0.0, self.dim)
        self.assertNotEqual(zero, ideal)


if __name__ == "__main__":
    unittest.main()
