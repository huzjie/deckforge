# -*- coding: utf-8 -*-
"""The design oracle: closed-form ground truth for every deck decision.

The oracle is what makes the pipeline *verifiable*. Instead of a learned reward
model or human review, every outline point maps to a unique deck element through
a deterministic rule, and every spec is checked against that mapping by a
program. This is the "可验证奖励" (verifiable reward) backbone: no human
labelling, only rule-based checks over a deterministic layout model.
"""
from __future__ import annotations

from ..utils.rng import stable_int


class DesignWorld:
    """Closed-form ground truth over synthetic slide decks."""

    def refer_to_element(self, deck, refer):
        """Map a natural-language refer to a unique element id, deterministically.

        Resolution order: exact eid -> exact label -> substring match -> seeded
        fallback. The fallback only ever triggers on malformed refers (so a well-
        formed outline always hits the first three branches).
        """
        el = deck.by_eid(refer)
        if el:
            return el.eid
        el = deck.by_label(refer)
        if el:
            return el.eid
        for e in deck.elements:
            if refer in e.label or (e.label and e.label in refer):
                return e.eid
        return deck.elements[
            stable_int("refer-fallback:%s" % refer, 0, len(deck.elements) - 1)
        ].eid

    def expected_spec(self, outline, deck):
        """Ground-truth ``(etype, eid)`` sequence for an outline's points."""
        return [(etype, self.refer_to_element(deck, refer))
                for (etype, refer) in outline["points"]]

    def spec_correct(self, pred_spec, expected_spec):
        """A spec is correct iff both the element type and the target match."""
        return pred_spec == expected_spec

    def deck_complete(self, pred_spec, expected_spec):
        """A deck is complete iff every point is correct."""
        return len(pred_spec) == len(expected_spec) and all(
            self.spec_correct(p, e) for p, e in zip(pred_spec, expected_spec)
        )
