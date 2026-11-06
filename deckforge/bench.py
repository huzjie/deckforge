# -*- coding: utf-8 -*-
"""Benchmarks: skill-driven metric table + monotonicity summary + repair gain."""
from __future__ import annotations

from .kit import build_kit
from .core.deck import render_deck, Deck
from .training.repair import repair_elements


def run_skill_table(cfg):
    """Aggregate the four deck-generation metrics vs skill."""
    kit = build_kit(cfg)
    engine = kit["engine"]
    rows = []
    for s in cfg["bench"]["skills"]:
        r = engine.run_all(s)
        rows.append({
            "skill": s,
            "layout_acc": r["layout_acc"],
            "design_acc": r["design_acc"],
            "deck_success": r["deck_success"],
            "score": r["score"],
        })
    return rows


def summarize(table):
    a, b = table[0], table[-1]
    return {
        "layout_acc": (a["layout_acc"], b["layout_acc"]),
        "design_acc": (a["design_acc"], b["design_acc"]),
        "deck_success": (a["deck_success"], b["deck_success"]),
        "score": (a["score"], b["score"]),
    }


def check_monotone(table):
    """Verify all four metrics are non-decreasing across the skill axis."""
    def inc(get):
        return all(get(table[i]) <= get(table[i + 1]) + 1e-9
                   for i in range(len(table) - 1))

    return {
        "layout_acc_inc": inc(lambda r: r["layout_acc"]),
        "design_acc_inc": inc(lambda r: r["design_acc"]),
        "deck_success_inc": inc(lambda r: r["deck_success"]),
        "score_inc": inc(lambda r: r["score"]),
    }


def _build_broken_decks(cfg, n=8):
    """Build a deterministic set of broken decks (vertical band jitter).

    Only the vertical position is jittered, so every defect is a zone violation
    or a vertical overlap -- exactly the two defect classes the repair harness
    is designed to detect and patch. Horizontal positions are left canonical.
    """
    from .utils.rng import stable_rand
    decks = []
    templates = ["pitch", "report", "tutorial", "metrics", "roadmap"]
    for i in range(n):
        template = templates[i % len(templates)]
        base = render_deck(seed="broken:%d" % i, template=template,
                           grid_w=cfg["model"]["grid_w"], grid_h=cfg["model"]["grid_h"])
        rnd = stable_rand("jitter:%d" % i)
        # Jitter every element's vertical position so zone violations and
        # vertical overlaps appear, while keeping horizontal positions intact.
        for el in base.elements:
            x0, y0, x1, y1 = el.bbox
            dy = rnd.uniform(-0.12, 0.12)
            el.bbox = (x0, y0 + dy, x1, y1 + dy)
        decks.append(base)
    return decks


def run_repair_gain(cfg, n=8):
    """Measure the closed-form repair gain over a set of broken decks."""
    from .training.repair import Repairer, deck_is_valid
    from .world.oracle import DesignWorld
    decks = _build_broken_decks(cfg, n)
    before = sum(1 for d in decks if not deck_is_valid(d.elements))
    repairer = Repairer(DesignWorld())
    res = repairer.repair_gain(decks, seed="bench-repair")
    after_invalid = sum(1 for d in decks if not deck_is_valid(d.elements))
    return {
        "broken_before": before,
        "broken_after": after_invalid,
        "fixed": res["fixed"],
        "gain": res["gain"],
        "n": len(decks),
    }
