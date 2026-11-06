# -*- coding: utf-8 -*-
"""Verifiable reward: per-element checks."""
from __future__ import annotations

import unittest

from deckforge.kit import build_kit
from deckforge.config import load_config


class TestVerifier(unittest.TestCase):
    def setUp(self):
        self.kit = build_kit(load_config())
        self.verifier = self.kit["verifier"]

    def test_mean_reward_at_oracle(self):
        self.assertGreaterEqual(self.verifier.mean_reward(1.0), 0.9999)

    def test_verify_element_accepted(self):
        deck = self.kit["corpus"]["templates"]["pitch"]
        target = deck.by_label("headline")
        r = self.verifier.verify_element("title", "title", target.center,
                                         "title", "title", target)
        self.assertTrue(r["accepted"])
        self.assertEqual(r["reward"], 1.0)

    def test_verify_element_rejected(self):
        deck = self.kit["corpus"]["templates"]["pitch"]
        target = deck.by_label("headline")
        r = self.verifier.verify_element("bullet", "points", (0.01, 0.01),
                                         "title", "title", target)
        self.assertFalse(r["accepted"])
        self.assertEqual(r["reward"], 0.0)


if __name__ == "__main__":
    unittest.main()
