# -*- coding: utf-8 -*-
"""Element vocabulary and layout-zone validity for deck generation.

A slide element is one of a small, fixed set. Each element type is only *legal*
in a specific vertical zone (a title must be at the top, a footer at the bottom,
content in the middle). The verifier uses this map to reject malformed layouts,
which is part of what makes the reward "verifiable" rather than a fuzzy score.
"""
from __future__ import annotations

from .deck import ELEMENT_TYPES

# Which vertical band (normalized y) each element type must occupy. A layout
# element outside its band is a design error the checker flags. The bands are
# disjoint (with clear gaps) so a repair snap always lands in a non-overlapping
# position relative to the neighbouring band.
LAYOUT_ZONE = {
    "title": (0.00, 0.17),
    "subtitle": (0.18, 0.28),
    "bullet": (0.30, 0.76),
    "image": (0.30, 0.76),
    "chart": (0.30, 0.76),
    "table": (0.30, 0.76),
    "code": (0.30, 0.76),
    "caption": (0.77, 0.85),
    "footer": (0.86, 1.00),
}


def validate_element(etype, bbox):
    """Return True if ``etype`` sits inside its legal vertical zone."""
    if etype not in LAYOUT_ZONE:
        return False
    lo, hi = LAYOUT_ZONE[etype]
    _, y0, _, y1 = bbox
    return lo - 1e-9 <= y0 and y1 <= hi + 1e-9


def count_conflicts(elements):
    """Count pairwise bounding-box overlaps among ``elements``.

    Overlap (two elements painting the same cells) is the primary layout bug a
    repair harness must fix; a valid deck has zero conflicts.
    """
    n = 0
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            if elements[i].overlaps(elements[j]):
                n += 1
    return n


def all_valid_elements(elements):
    """Return (all_valid, bad_indices) for a list of ``Element`` objects."""
    bad = []
    for i, el in enumerate(elements):
        if not validate_element(el.etype, el.bbox):
            bad.append(i)
    return not bad, bad
