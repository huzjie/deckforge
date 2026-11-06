# -*- coding: utf-8 -*-
"""Semantic encoder: deck element -> deterministic embedding + outline alignment.

This is the "design stage" half of deck generation. Every element gets a
deterministic embedding derived from its (type, label) so that a natural-language
outline point can be **aligned** to the right element in the same vector space
(no training-time alignment table). The deck vector aggregates all elements.

The trainable "skill" enters here: at skill=1.0 the refer embedding equals the
target element's embedding exactly (so cosine matching picks it); at skill=0.0
the refer embedding is pure deterministic noise (so matching is an independent
coin-flip over the candidate elements).
"""
from __future__ import annotations

from ..utils.rng import stable_vector
from ..utils.linalg import cosine


def encode_element(el, dim):
    """Deterministic embedding of an element from its type + label."""
    return stable_vector("%s:%s" % (el.etype, el.label), dim, -1.0, 1.0)


def encode_deck(deck, dim):
    """Return (deck_vector, {eid: element_vector}) for a deck."""
    vecs = {el.eid: encode_element(el, dim) for el in deck.elements}
    if not vecs:
        return [0.0] * dim, {}
    scene = [0.0] * dim
    for v in vecs.values():
        for i in range(dim):
            scene[i] += v[i]
    n = len(vecs)
    scene = [x / n for x in scene]
    return scene, vecs


def refer_embedding(refer, ideal, skill, dim):
    """Blend the ideal (ground-truth) element embedding with noise by skill.

    skill=1.0 -> exact ideal; skill=0.0 -> pure deterministic noise. This is the
    single knob that makes every downstream metric monotone in skill.
    """
    noise = stable_vector("noise:%s" % refer, dim, -1.0, 1.0)
    return [ideal[i] * skill + noise[i] * (1.0 - skill) for i in range(dim)]


def cosine_match(vecs, query):
    """Return the eid whose embedding has the highest cosine similarity to query."""
    best, best_sim = None, -2.0
    for eid, v in vecs.items():
        s = cosine(v, query)
        if s > best_sim:
            best, best_sim = eid, s
    return best
