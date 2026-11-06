# -*- coding: utf-8 -*-
"""Repair a broken deck and report the detect/locate/patch result."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckforge.config import load_config
from deckforge.bench import _build_broken_decks
from deckforge.training.repair import detect, repair_elements, deck_is_valid


def main():
    cfg = load_config()
    decks = _build_broken_decks(cfg, 4)
    for deck in decks:
        report = detect(deck.elements)
        print("template=%s defects: out_of_zone=%s overlaps=%s" % (
            deck.template, report["out_of_zone"], report["overlaps"]))
        repair_elements(deck.elements)
        print("  -> after repair, valid=%s" % deck_is_valid(deck.elements))


if __name__ == "__main__":
    main()
