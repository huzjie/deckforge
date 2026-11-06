# -*- coding: utf-8 -*-
"""Locate a deck element for a natural-language outline point."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckforge.kit import build_kit
from deckforge.config import load_config


def main():
    kit = build_kit(load_config())
    deck = kit["corpus"]["templates"]["pitch"]
    layouter = kit["engine"].layouter

    for refer in ("headline", "points", "image"):
        target_eid = kit["world"].refer_to_element(deck, refer)
        eid, (x, y) = layouter.locate(deck, refer, 1.0, target_eid)
        print("refer=%-9s -> element=%s point=(%.3f, %.3f)" % (refer, eid, x, y))


if __name__ == "__main__":
    main()
