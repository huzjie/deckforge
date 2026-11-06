# -*- coding: utf-8 -*-
"""Design stage: outline -> ordered design spec (element type + target element).

An outline is a goal expressed over a deck (e.g. "pitch": headline, subtitle,
bullet points, image, footer). The designer maps each outline point to a concrete
element type with a target element. The oracle branch emits the exact expected
spec; the baseline emits a random element type and a random target element
(independent coin-flip).
"""
from __future__ import annotations

from ..utils.rng import stable_rand
from .deck import ELEMENT_TYPES


class Designer:
    """Plan an outline into an element spec at a given skill."""

    def __init__(self, world):
        self.world = world

    def design(self, outline, deck, skill):
        """Return a list of ``(etype, eid)`` for every point in ``outline``."""
        out = []
        for i, (etype, refer) in enumerate(outline["points"]):
            target_eid = self.world.refer_to_element(deck, refer)
            if skill >= 1.0 - 1e-12:
                out.append((etype, target_eid))
            else:
                rnd = stable_rand("design-base:%s:%d" % (outline["id"], i))
                rnd_etype = ELEMENT_TYPES[rnd.randrange(len(ELEMENT_TYPES))]
                rnd_eid = deck.elements[rnd.randrange(len(deck.elements))].eid
                out.append((rnd_etype, rnd_eid))
        return out
