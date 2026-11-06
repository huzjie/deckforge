# -*- coding: utf-8 -*-
"""Repair harness: detect / locate / patch / revalidate."""
from __future__ import annotations

import unittest

from deckforge.training.repair import (Repairer, repair_elements, deck_is_valid,
                                       detect)
from deckforge.world.oracle import DesignWorld
from deckforge.bench import _build_broken_decks
from deckforge.config import load_config


class TestRepair(unittest.TestCase):
    def test_broken_decks_repaired(self):
        cfg = load_config()
        decks = _build_broken_decks(cfg, 8)
        repairer = Repairer(DesignWorld())
        res = repairer.repair_gain(decks, seed="test")
        self.assertEqual(res["fixed"], res["before"])
        self.assertEqual(res["after"], 0)
        self.assertEqual(res["gain"], 1.0)

    def test_detect_reports(self):
        cfg = load_config()
        decks = _build_broken_decks(cfg, 4)
        broken = [d for d in decks if not deck_is_valid(d.elements)]
        self.assertTrue(broken)
        report = detect(broken[0].elements)
        self.assertIsInstance(report["out_of_zone"], list)
        self.assertIsInstance(report["overlaps"], list)

    def test_repair_idempotent(self):
        cfg = load_config()
        decks = _build_broken_decks(cfg, 4)
        deck = decks[0]
        repair_elements(deck.elements, seed="test")
        self.assertTrue(deck_is_valid(deck.elements))
        repair_elements(deck.elements, seed="test")
        self.assertTrue(deck_is_valid(deck.elements))


if __name__ == "__main__":
    unittest.main()
