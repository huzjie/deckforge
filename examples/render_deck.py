# -*- coding: utf-8 -*-
"""Render a deterministic synthetic slide deck as a text grid."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckforge.core.deck import render_deck


def main():
    deck = render_deck(seed="demo", template="pitch", grid_w=40, grid_h=24)
    print("template:", deck.template)
    print("elements:")
    for el in deck.elements:
        print("  %-9s %-8s %-8s bbox=%s" % (el.eid, el.etype, el.label,
                                             [round(v, 3) for v in el.bbox]))
    print("\nrendered grid:")
    for row in deck.grid:
        print(row)


if __name__ == "__main__":
    main()
