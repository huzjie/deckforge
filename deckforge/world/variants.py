# -*- coding: utf-8 -*-
"""Deterministic outline variants: rotate (and occasionally drop) a template's
points so the corpus exercises varied element orders, not a single memorizable path.

The oracle always sees the *post-variant* point list, so a variant is never
"wrong" -- it just changes the ground-truth target the model must recover.
"""
from __future__ import annotations


def build_point_variants(template, index):
    """Return a deterministic variation of ``template`` based on ``index``.

    * index % 3 == 0 -> identity (keep the canonical order)
    * index % 3 == 1 -> left-rotate by one point
    * index % 3 == 2 -> left-rotate by two points
    """
    points = list(template)
    if not points:
        return points
    rot = index % 3
    if rot == 0:
        return points
    return points[rot:] + points[:rot]
