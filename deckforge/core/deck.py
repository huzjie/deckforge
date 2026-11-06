# -*- coding: utf-8 -*-
"""Synthetic slide-deck rendering -- the "coding stage" observation.

A zero-dependency stand-in for a real presentation engine: instead of pixels we
render a deterministic **text grid** in which every slide element occupies a
rectangular bounding box. The grid is what the layout checker consumes; the
element list (id, type, label, bbox) is the *semantic* ground truth the oracle
knows.

The layout is fully deterministic: given a ``template`` name and a ``seed``, the
same deck is always reproduced bit-for-bit. This is the precondition for a
**verifiable reward**: two independent runs of the same outline must see the
same rendered deck and the same ground-truth spec.

This mirrors IBM Palette's "separate design and coding stages": the *design*
stage emits the element spec (types + labels), the *coding* stage materializes
it into a concrete, checkable layout (bboxes + text grid). Both stages are
deterministic so a program can verify the result.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..utils.rng import stable_rand

# Slide element kinds a synthetic deck can contain.
ELEMENT_TYPES = ["title", "subtitle", "bullet", "image", "chart", "table", "code", "footer", "caption"]

# Per-template element specs: (element id, type, label). Labels are unique within
# a deck so a natural-language outline point can map to exactly one element.
TEMPLATES = {
    "pitch": [
        ("title", "title", "headline"),
        ("subtitle", "subtitle", "subtitle"),
        ("bullet", "bullet", "points"),
        ("image", "image", "image"),
        ("footer", "footer", "footer"),
    ],
    "report": [
        ("title", "title", "headline"),
        ("chart", "chart", "chart"),
        ("bullet", "bullet", "points"),
        ("table", "table", "table"),
        ("footer", "footer", "footer"),
    ],
    "tutorial": [
        ("title", "title", "headline"),
        ("subtitle", "subtitle", "subtitle"),
        ("code", "code", "code"),
        ("caption", "caption", "caption"),
        ("footer", "footer", "footer"),
    ],
    "metrics": [
        ("title", "title", "headline"),
        ("chart", "chart", "chart"),
        ("chart", "chart", "chart2"),
        ("caption", "caption", "caption"),
        ("footer", "footer", "footer"),
    ],
    "roadmap": [
        ("title", "title", "headline"),
        ("bullet", "bullet", "points"),
        ("bullet", "bullet", "milestones"),
        ("image", "image", "image"),
        ("footer", "footer", "footer"),
    ],
}

# Marker glyph used in the text grid for each element type (visual cue only).
GLYPHS = {
    "title": "=",
    "subtitle": "-",
    "bullet": ".",
    "image": "#",
    "chart": "%",
    "table": "+",
    "code": "~",
    "footer": "_",
    "caption": "*",
}


@dataclass
class Element:
    eid: str
    etype: str
    label: str
    bbox: tuple  # (x0, y0, x1, y1) in normalized [0,1] coordinates
    value: str = ""

    @property
    def center(self):
        x0, y0, x1, y1 = self.bbox
        return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)

    @property
    def width(self):
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self):
        return self.bbox[3] - self.bbox[1]

    def contains(self, x, y):
        x0, y0, x1, y1 = self.bbox
        return x0 <= x <= x1 and y0 <= y <= y1

    def overlaps(self, other):
        """Axis-aligned bounding-box intersection (for layout-conflict checks)."""
        a = self.bbox
        b = other.bbox
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


@dataclass
class Deck:
    template: str
    title: str
    elements: list
    grid: list = field(default_factory=list)  # rendered text grid (list of str rows)

    def by_eid(self, eid):
        for el in self.elements:
            if el.eid == eid:
                return el
        return None

    def by_label(self, label):
        for el in self.elements:
            if el.label == label:
                return el
        return None


# Vertical zone bands (normalized) used to place each element type.
# Title/subtitle live in the top band, footer in the bottom band, and the
# content types fill the middle. Keeping bands deterministic is what lets the
# layout checker verify "no overflow, no overlap, no empty slide".
_BAND = {
    "title": (0.03, 0.15),
    "subtitle": (0.19, 0.26),
    "caption": (0.78, 0.84),
    "footer": (0.87, 0.94),
}


def _layout(template, seed, grid_w, grid_h):
    """Deterministic placement of a template's elements into normalized bboxes."""
    specs = TEMPLATES[template]
    rng = stable_rand("%s:%s:layout" % (template, seed))
    elements = []
    for i, (eid, etype, label) in enumerate(specs):
        if etype in _BAND:
            y0, y1 = _BAND[etype]
        else:
            # Content types share the middle band, stacked in order.
            top = 0.31
            bottom = 0.75
            n_content = sum(1 for (_i, t, _l) in specs if t not in _BAND)
            band = (bottom - top) / max(n_content, 1)
            order = sum(1 for (_i, t, _l) in specs[:i] if t not in _BAND)
            y0 = top + band * order + band * 0.08
            y1 = top + band * (order + 1) - band * 0.08
        # Width varies by type: title/footer full-bleed, bullet/image/chart
        # narrower (left or right column), table/code/caption full width.
        if etype in ("title", "subtitle", "footer", "table", "code", "caption"):
            x0 = 0.06 + rng.uniform(0.0, 0.02)
            x1 = 0.94 - rng.uniform(0.0, 0.02)
        elif etype == "bullet":
            x0 = 0.07 + rng.uniform(0.0, 0.03)
            x1 = x0 + 0.40
        elif etype == "image":
            x0 = 0.52 + rng.uniform(0.0, 0.03)
            x1 = x0 + 0.40
        else:  # chart
            x0 = 0.07 + rng.uniform(0.0, 0.03)
            x1 = x0 + 0.55
        elements.append(Element(eid=eid, etype=etype, label=label, bbox=(x0, y0, x1, y1)))
    return elements


def _render_grid(elements, template, grid_w, grid_h):
    """Paint elements into a text grid using their type glyphs."""
    rows = [[" "] * grid_w for _ in range(grid_h)]
    title = ("%s" % template).upper()[: grid_w]
    for j, ch in enumerate(title):
        rows[0][j] = ch
    for el in elements:
        x0, y0, x1, y1 = el.bbox
        c0 = max(0, int(x0 * grid_w))
        c1 = min(grid_w - 1, int(x1 * grid_w))
        r0 = max(1, int(y0 * grid_h))
        r1 = min(grid_h - 1, int(y1 * grid_h))
        glyph = GLYPHS.get(el.etype, "?")
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                rows[r][c] = glyph
    return ["".join(row) for row in rows]


def render_deck(seed="default", template=None, grid_w=40, grid_h=24):
    """Build a deterministic synthetic deck for ``template`` (or a seeded choice)."""
    if template is None or template not in TEMPLATES:
        templates = list(TEMPLATES.keys())
        template = templates[stable_rand("pick:%s" % seed).randrange(len(templates))]
    elements = _layout(template, seed, grid_w, grid_h)
    grid = _render_grid(elements, template, grid_w, grid_h)
    return Deck(template=template, title=template, elements=elements, grid=grid)
