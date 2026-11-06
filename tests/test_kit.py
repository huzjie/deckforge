# -*- coding: utf-8 -*-
"""Kit assembly."""
from __future__ import annotations

import unittest

from deckforge.kit import build_kit
from deckforge.config import load_config


class TestKit(unittest.TestCase):
    def test_kit_keys(self):
        kit = build_kit(load_config())
        for key in ("cfg", "corpus", "world", "engine", "verifier", "repairer"):
            self.assertIn(key, kit)

    def test_kit_engine_matches_corpus(self):
        kit = build_kit(load_config())
        r = kit["engine"].run_all(1.0)
        self.assertEqual(r["n_decks"], len(kit["corpus"]["decks"]))


if __name__ == "__main__":
    unittest.main()
