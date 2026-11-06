# -*- coding: utf-8 -*-
"""Print the four skill-driven metric curves (no plotting library needed)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckforge.config import load_config
from deckforge.bench import run_skill_table


def main():
    cfg = load_config()
    table = run_skill_table(cfg)
    print("%-6s %-10s %-10s %-12s %-8s" % ("skill", "layout_acc", "design_acc", "deck_success", "score"))
    for r in table:
        print("%-6.2f %-10.4f %-10.4f %-12.4f %-8.4f" % (
            r["skill"], r["layout_acc"], r["design_acc"], r["deck_success"], r["score"]))


if __name__ == "__main__":
    main()
