# -*- coding: utf-8 -*-
"""Programmatic verifier: turn closed-form checks into a verifiable reward.

This is the "可验证奖励" (verifiable reward) idea from Palette's "checked
repairs" made concrete. Instead of a learned reward model or human labels, a
reward is produced by *checking the model's spec against a rule-based oracle*:

* element type must match the expected type;
* target element must match the expected element;
* predicted bbox point must land inside the expected element's bounding box.

An element earns reward 1.0 only if all three hold. Any element the verifier
cannot confirm is rewarded 0 -- the mechanism that suppresses "hallucinated"
elements (targeting an element that does not exist) during training.
"""
from __future__ import annotations


class Verifier:
    def __init__(self, engine, world):
        self.engine = engine
        self.world = world

    def verify_element(self, pred_etype, pred_eid, pred_point, expected_etype,
                       expected_eid, target_el):
        """Return a dict of per-condition checks + the binary element reward."""
        type_ok = pred_etype == expected_etype
        target_ok = pred_eid == expected_eid
        point_ok = bool(target_el.contains(pred_point[0], pred_point[1]))
        accepted = type_ok and target_ok and point_ok
        return {
            "accepted": accepted,
            "reward": 1.0 if accepted else 0.0,
            "type_ok": type_ok,
            "target_ok": target_ok,
            "point_ok": point_ok,
        }

    def verify_deck(self, outline, deck, skill):
        """Verify every point of an outline and return per-point verdicts."""
        results = []
        for i, (etype, refer) in enumerate(outline["points"]):
            target_eid = self.world.refer_to_element(deck, refer)
            target_el = deck.by_eid(target_eid)
            trace = self.engine.run_deck(outline, skill)["trace"][i]
            results.append(self.verify_element(
                trace["etype"], trace["element"], trace["point"],
                etype, target_eid, target_el))
        return results

    def mean_reward(self, skill):
        """Mean verifiable reward (the point-level composite) at a given skill."""
        return self.engine.run_all(skill)["score"]
