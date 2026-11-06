# -*- coding: utf-8 -*-
"""Config defaults + recipe merge."""
from __future__ import annotations

import os
import tempfile
import unittest

from deckforge.config import load_config, DEFAULTS


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = load_config()
        self.assertEqual(cfg["model"]["skill"], 0.5)
        self.assertEqual(cfg["model"]["grid_w"], 40)
        self.assertIn("n_decks", cfg["world"])
        self.assertEqual(cfg["bench"]["skills"], [0.0, 0.25, 0.5, 0.75, 1.0])

    def test_recipe_merge(self):
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("model:\n  skill: 0.9\n")
            cfg = load_config(path)
            self.assertEqual(cfg["model"]["skill"], 0.9)
            self.assertEqual(cfg["model"]["dim"], DEFAULTS["model"]["dim"])
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
