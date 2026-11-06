# -*- coding: utf-8 -*-
"""Deterministic corpus: synthetic decks + outline set (synthetic training data).

Everything is reproducible from string keys, so a benchmark run is stable across
machines and processes -- which is what lets the verifier and the benchmark make
exact, repeatable claims. This mirrors Palette's "synthetic training data": every
(outline -> design spec -> rendered deck) triple is generated programmatically
and deterministically, giving an unlimited labelled training set with zero human
labelling.
"""
from __future__ import annotations

from ..core.deck import render_deck, TEMPLATES
from .variants import build_point_variants

# Outline templates: template -> sequence of (element_type, refer). The refer is
# an element label (unique within the deck), so the oracle resolves it exactly.
OUTLINE_TEMPLATES = {
    "pitch": [
        ("title", "headline"),
        ("subtitle", "subtitle"),
        ("bullet", "points"),
        ("image", "image"),
        ("footer", "footer"),
    ],
    "report": [
        ("title", "headline"),
        ("chart", "chart"),
        ("bullet", "points"),
        ("table", "table"),
        ("footer", "footer"),
    ],
    "tutorial": [
        ("title", "headline"),
        ("subtitle", "subtitle"),
        ("code", "code"),
        ("caption", "caption"),
        ("footer", "footer"),
    ],
    "metrics": [
        ("title", "headline"),
        ("chart", "chart"),
        ("chart", "chart2"),
        ("caption", "caption"),
        ("footer", "footer"),
    ],
    "roadmap": [
        ("title", "headline"),
        ("bullet", "points"),
        ("bullet", "milestones"),
        ("image", "image"),
        ("footer", "footer"),
    ],
}


def build_templates(grid_w, grid_h):
    """One deterministic rendered deck per template."""
    decks = {}
    for template in TEMPLATES:
        decks[template] = render_deck(seed="corpus:%s" % template, template=template,
                                      grid_w=grid_w, grid_h=grid_h)
    return decks


def build_decks(n_decks):
    """A deterministic outline set cycling through the templates with varied point order."""
    templates = list(TEMPLATES.keys())
    decks = []
    for i in range(n_decks):
        template = templates[i % len(templates)]
        base = OUTLINE_TEMPLATES[template]
        points = build_point_variants(base, i)
        decks.append({"id": "d%02d" % i, "template": template, "points": points})
    return decks


def build_corpus(cfg):
    """Assemble the full deterministic corpus from config."""
    w = cfg["world"]
    m = cfg["model"]
    templates = build_templates(m["grid_w"], m["grid_h"])
    decks = build_decks(w.get("n_decks", 20))
    return {"decks": decks, "templates": templates}
