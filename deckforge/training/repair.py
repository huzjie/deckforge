# -*- coding: utf-8 -*-
"""Repair harness: the "checked repairs" loop from IBM Palette.

Palette reports a 3.5-point average improvement from its repair harness on
PresentBench. This is a zero-dependency reproduction of that loop: a deck is
rendered, a program **checks** it (overlap / out-of-zone / empty), **locates**
the offending elements, **patches** them deterministically, and **revalidates**.

The loop is fully closed-form: given the same broken deck, the same patch always
produces the same repaired deck, so the "repair gain" is an exact, repeatable
number rather than a fuzzy human score. The patch preserves each element's
identity and horizontal extent -- it only corrects the vertical placement
(zone snap + deterministic re-stack), which is exactly the class of defect a
deck layout checker can prove.
"""
from __future__ import annotations

from ..core.elements import LAYOUT_ZONE, count_conflicts
from ..core.deck import TEMPLATES


# Canonical vertical bands (must match the renderer in core/deck.py). Elements
# in these fixed bands are snapped back here during repair.
_FIXED_BAND = {
    "title": (0.03, 0.15),
    "subtitle": (0.19, 0.26),
    "caption": (0.78, 0.84),
    "footer": (0.87, 0.94),
}

# Content types share the middle band and are re-stacked in canonical order.
_CONTENT_TYPES = ("bullet", "image", "chart", "table", "code")
_CONTENT_TOP = 0.31
_CONTENT_BOTTOM = 0.75


def _out_of_zone(el):
    """True if the element sits outside its legal vertical band."""
    if el.etype not in LAYOUT_ZONE:
        return False
    lo, hi = LAYOUT_ZONE[el.etype]
    _, y0, _, y1 = el.bbox
    return not (lo - 1e-9 <= y0 and y1 <= hi + 1e-9)


def deck_is_valid(elements):
    """A deck is valid iff it has no overlaps and no out-of-zone element."""
    if count_conflicts(elements) != 0:
        return False
    return not any(_out_of_zone(e) for e in elements)


def detect(elements):
    """Return a diagnostic report: out-of-zone ids + overlapping id pairs."""
    out_of_zone = [el.eid for el in elements if _out_of_zone(el)]
    overlaps = []
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            if elements[i].overlaps(elements[j]):
                overlaps.append((elements[i].eid, elements[j].eid))
    return {"out_of_zone": out_of_zone, "overlaps": overlaps}


def _patch(elements):
    """Deterministically correct vertical placement while preserving identity
    and horizontal extent.

    * fixed-band elements (title/subtitle/caption/footer) are snapped back to
      their canonical band;
    * content elements are re-stacked in their canonical list order inside the
      middle band.
    """
    # 1. snap fixed-band elements.
    for el in elements:
        if el.etype in _FIXED_BAND:
            y0, y1 = _FIXED_BAND[el.etype]
            x0, _, x1, _ = el.bbox
            el.bbox = (x0, y0, x1, y1)
    # 2. re-stack content elements in canonical order (order of appearance).
    contents = [el for el in elements if el.etype in _CONTENT_TYPES]
    n = len(contents)
    if n:
        band = (_CONTENT_BOTTOM - _CONTENT_TOP) / n
        for i, el in enumerate(contents):
            y0 = _CONTENT_TOP + band * i + band * 0.08
            y1 = _CONTENT_TOP + band * (i + 1) - band * 0.08
            x0, _, x1, _ = el.bbox
            el.bbox = (x0, y0, x1, y1)
    return elements


def repair_elements(elements, seed="repair", rounds=1):
    """Detect, locate, and patch layout conflicts in a list of ``Element``s.

    Returns the (possibly mutated) element list. The patch is idempotent for the
    same seed so the repair gain is reproducible. ``seed`` and ``rounds`` are
    kept for API compatibility; the patch is deterministic in one pass.
    """
    for _ in range(rounds):
        if deck_is_valid(elements):
            break
        _patch(elements)
        if deck_is_valid(elements):
            break
    return elements


class Repairer:
    """Measure the closed-form repair gain over a corpus of broken decks."""

    def __init__(self, world):
        self.world = world

    @staticmethod
    def deck_conflict_count(deck):
        return count_conflicts(deck.elements)

    def repair_gain(self, broken_decks, seed="repair"):
        """Fraction of broken decks that become valid after repair."""
        if not broken_decks:
            return {"before": 0, "after": 0, "fixed": 0, "gain": 0.0, "n": 0}
        before = sum(1 for d in broken_decks if not deck_is_valid(d.elements))
        fixed = 0
        for deck in broken_decks:
            repair_elements(deck.elements, seed=seed)
            if deck_is_valid(deck.elements):
                fixed += 1
        n = len(broken_decks)
        after = sum(1 for d in broken_decks if not deck_is_valid(d.elements))
        return {
            "before": before,
            "after": after,
            "fixed": fixed,
            "gain": (fixed / before) if before else 1.0,
            "n": n,
        }
