# -*- coding: utf-8 -*-
"""Engine: oracle reproduction + monotone skill curves."""
from __future__ import annotations

import unittest

from deckforge.kit import build_kit
from deckforge.config import load_config


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.kit = build_kit(load_config())
        self.engine = self.kit["engine"]

    def test_oracle_reproduction(self):
        r = self.engine.run_all(1.0)
        self.assertGreaterEqual(r["layout_acc"], 0.9999)
        self.assertGreaterEqual(r["design_acc"], 0.9999)
        self.assertGreaterEqual(r["deck_success"], 0.9999)
        self.assertGreaterEqual(r["score"], 0.9999)

    def test_monotone_skill_curve(self):
        table = self.engine.run_all_skill_table([0.0, 0.25, 0.5, 0.75, 1.0])
        for key in ("layout_acc", "design_acc", "deck_success", "score"):
            vals = [r[key] for r in table]
            for i in range(len(vals) - 1):
                self.assertLessEqual(vals[i], vals[i + 1] + 1e-9, key)

    def test_baseline_below_oracle(self):
        base = self.engine.run_all(0.0)
        full = self.engine.run_all(1.0)
        self.assertLess(base["score"], full["score"])

    def test_embedding_diagnostic_separated(self):
        d = self.engine.embedding_diagnostic()
        self.assertLess(d["mean_cross_cosine"], 0.5)

    def test_run_deck_trace(self):
        outline = self.kit["corpus"]["decks"][0]
        res = self.engine.run_deck(outline, 1.0)
        self.assertTrue(res["success"])
        self.assertEqual(len(res["trace"]), len(outline["points"]))


if __name__ == "__main__":
    unittest.main()
