# -*- coding: utf-8 -*-
"""Training: monotone skill axis + verifiable reward."""
from __future__ import annotations

import unittest

from deckforge.training.trainer import SkillTrainer, RewardTrainer
from deckforge.kit import build_kit
from deckforge.config import load_config


class TestTrainer(unittest.TestCase):
    def test_skill_trainer_monotone(self):
        t = SkillTrainer(0.0, lr=0.05)
        prev = 0.0
        for _ in range(20):
            rec = t.train_step()
            self.assertGreaterEqual(rec["skill"], prev)
            self.assertGreaterEqual(rec["delta"], 0.0)
            prev = rec["skill"]
        self.assertLessEqual(t.skill, 1.0)

    def test_reward_trainer_monotone(self):
        kit = build_kit(load_config())
        trainer = RewardTrainer(kit["verifier"], skill=0.0, lr=0.05)
        for _ in range(10):
            trainer.step()
        self.assertTrue(trainer.is_monotone())


if __name__ == "__main__":
    unittest.main()
