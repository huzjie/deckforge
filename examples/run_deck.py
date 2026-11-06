# -*- coding: utf-8 -*-
"""Generate a deck end-to-end (closed loop) and print the trace."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckforge.kit import build_kit
from deckforge.config import load_config


def main():
    kit = build_kit(load_config())
    outline = kit["corpus"]["decks"][0]
    res = kit["engine"].run_deck(outline, skill=1.0)
    print("deck=%s template=%s success=%s" % (outline["id"], outline["template"], res["success"]))
    for tr in res["trace"]:
        mark = "OK" if tr["ok"] else "!!"
        print("  [%s] %s -> %s @ (%s, %s)" % (mark, tr["etype"], tr["element"],
                                              tr["point"][0], tr["point"][1]))


if __name__ == "__main__":
    main()
