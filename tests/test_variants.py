# -*- coding: utf-8 -*-
"""Deterministic outline variants."""
from __future__ import annotations

import unittest

from deckforge.world.variants import build_point_variants


class TestVariants(unittest.TestCase):
    def test_identity(self):
        base = [("title", "a"), ("bullet", "b")]
        self.assertEqual(build_point_variants(base, 0), base)

    def test_rotate(self):
        base = [("title", "a"), ("bullet", "b"), ("footer", "c")]
        self.assertEqual(build_point_variants(base, 1),
                         [("bullet", "b"), ("footer", "c"), ("title", "a")])

    def test_empty(self):
        self.assertEqual(build_point_variants([], 5), [])


if __name__ == "__main__":
    unittest.main()
