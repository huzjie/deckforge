# -*- coding: utf-8 -*-
"""Declarative task registry for the four deck-generation capabilities."""

TASKS = [
    {
        "id": "layout",
        "name": "Layout Placement",
        "desc": ("Given a natural-language outline point (e.g. 'headline'), return the "
                 "deck element and a bbox point that lands inside its bounding "
                 "box. The coding/render stage of deck generation."),
        "metrics": ["layout_acc"],
    },
    {
        "id": "design",
        "name": "Design Specification",
        "desc": ("Decompose an outline into an ordered design spec of (element type, "
                 "target element) -- title / bullet / chart / image / footer -- "
                 "and recover the ground-truth spec."),
        "metrics": ["design_acc"],
    },
    {
        "id": "completion",
        "name": "Closed-loop Completion",
        "desc": ("Generate an outline end-to-end against the layout oracle; a deck "
                 "succeeds only if every point is correct."),
        "metrics": ["deck_success"],
    },
    {
        "id": "reward",
        "name": "Verifiable Reward",
        "desc": ("Programmatically check each element (type + target + point) against "
                 "the oracle and emit a binary reward, giving a monotone training "
                 "signal that suppresses hallucinated elements."),
        "metrics": ["score"],
    },
    {
        "id": "repair",
        "name": "Checked Repair Harness",
        "desc": ("Detect, locate, and patch layout conflicts (overlap / out-of-zone) "
                 "in a closed-form loop, then revalidate. Mirrors Palette's repair "
                 "harness that adds +3.5 points on PresentBench."),
        "metrics": ["repair_gain"],
    },
]


def list_tasks():
    return TASKS


def get_task(name):
    for t in TASKS:
        if t["id"] == name:
            return t
    raise KeyError("unknown task: %s" % name)
