# -*- coding: utf-8 -*-
"""Deterministic corpus: templates + outline set."""
from __future__ import annotations

import unittest

from deckforge.world.corpus import build_corpus, OUTLINE_TEMPLATES, build_decks
from deckforge.config import load_config


class TestCorpus(unittest.TestCase):
    def test_build_corpus(self):
        cfg = load_config()
        corpus = build_corpus(cfg)
        self.assertEqual(len(corpus["templates"]), 5)
        self.assertEqual(len(corpus["decks"]), cfg["world"]["n_decks"])

    def test_outline_points_resolve(self):
        cfg = load_config()
        corpus = build_corpus(cfg)
        for outline in corpus["decks"]:
            deck = corpus["templates"][outline["template"]]
            for etype, refer in outline["points"]:
                el = deck.by_label(refer)
                self.assertIsNotNone(el, (outline["id"], refer))

    def test_build_decks_deterministic(self):
        a = build_decks(10)
        b = build_decks(10)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
