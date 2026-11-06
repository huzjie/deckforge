# -*- coding: utf-8 -*-
"""CLI smoke: doctor / bench / modes / run / train / repair run without error."""
from __future__ import annotations

import unittest

from deckforge.cli import main


class TestCli(unittest.TestCase):
    def test_doctor(self):
        main(["doctor"])  # raises SystemExit on failure

    def test_bench(self):
        main(["bench"])

    def test_modes(self):
        main(["modes"])

    def test_run(self):
        main(["run", "--deck", "d00", "--skill", "1.0"])

    def test_train(self):
        main(["train", "--steps", "3"])

    def test_repair(self):
        main(["repair", "--n", "4"])


if __name__ == "__main__":
    unittest.main()
