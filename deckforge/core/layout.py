# -*- coding: utf-8 -*-
"""Layout stage: outline point -> deck element -> concrete bbox.

This is the "coding stage" head. For a given outline point (e.g. ``headline``)
the model must return the element *and* a concrete bounding box. The oracle
branch aligns the point to the target element's embedding and returns its exact
bbox; the untrained baseline picks a random element and a random bbox (an
independent coin-flip, not an anti-oracle).

The benchmark switches between the two via a per-item threshold so that accuracy
rises monotonically in ``skill`` (see ``Engine``).
"""
from __future__ import annotations

from ..utils.rng import stable_rand
from .embed import encode_deck, encode_element, cosine_match


class Layouter:
    """Place elements on a deck given a natural-language refer and a skill."""

    def __init__(self, dim):
        self.dim = dim

    def locate(self, deck, refer, skill, target_eid):
        """Return (predicted_eid, (x, y)) for a refer at a given skill.

        ``target_eid`` is the ground-truth element id (known by the oracle); the
        model must not "see" it except through the skill-controlled branch below.
        """
        target_el = deck.by_eid(target_eid)
        _, vecs = encode_deck(deck, self.dim)

        if skill >= 1.0 - 1e-12:
            # Oracle: align refer to the ideal embedding, match it, return center.
            ideal = encode_element(target_el, self.dim)
            matched = cosine_match(vecs, ideal)
            return matched, target_el.center

        # Baseline: independent coin-flip -- random element + random point.
        rnd = stable_rand("layout-base:%s" % refer)
        eid = deck.elements[rnd.randrange(len(deck.elements))].eid
        return eid, (rnd.random(), rnd.random())

    def hit(self, deck, refer, skill, target_eid):
        """Return (predicted_eid, (x, y), hit_bool) where hit means the point is
        inside the ground-truth element's bounding box."""
        eid, (x, y) = self.locate(deck, refer, skill, target_eid)
        target_el = deck.by_eid(target_eid)
        return eid, (x, y), target_el.contains(x, y)
