# -*- coding: utf-8 -*-
"""deckforge: a zero-dependency slide-deck generation agent reference.

A pure-Python reference implementation of the idea behind IBM Palette's slide
generation model: instead of asking one LLM to "write a deck" end-to-end, we
model the whole pipeline as a small, verifiable system with **separate design
and coding stages**, **synthetic training data**, and a **checked repair
harness**:

* a **synthetic deck renderer** draws a deterministic slide (title / bullet /
  chart / image / footer) into a text grid -- the "coding stage" observation;
* a **semantic encoder** turns every element into a deterministic embedding and
  aligns a natural-language outline point (e.g. "headline") to it in the same
  space -- the "design stage" alignment;
* a **layout head** regresses element -> bbox point, with accuracy that rises
  monotonically as the model's "skill" goes from an untrained baseline
  (independent coin-flip) to the oracle;
* a **designer** turns an outline into an element spec (title / bullet / chart /
  image / footer), each point targetable to a deck element;
* a **closed-loop engine** generates an outline against a **closed-form layout
  oracle**, which is the single source of ground truth;
* a **repair harness** detects, locates, and patches layout conflicts (overlap /
  out-of-zone) then revalidates -- the "checked repairs" loop;
* a **programmatic verifier** turns every element's correctness into a
  **verifiable reward**, and a **skill trainer** climbs toward the oracle with an
  always-positive delta (so the benchmark curves are monotone by construction).

Pure Python, no numpy / torch / requests.
"""
from .version import __version__

__all__ = ["__version__"]
