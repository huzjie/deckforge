# -*- coding: utf-8 -*-
"""Runtime configuration with layered defaults (code default < recipe yaml < cli)."""
from __future__ import annotations

import copy

from .utils.yamlish import yaml_loads

# Defaults are deliberately small so a reference run stays interactive (<10s on
# a laptop) while still exercising every code path and every outline. The real
# Palette-class system uses a 20B design/coding model with synthetic training
# data and a checked repair harness; the reference keeps the same pipeline shape
# (design stage + coding/render stage + verifier + repair harness) at a
# laptop-friendly scale.
DEFAULTS = {
    "model": {
        "skill": 0.5,            # 0.0 (untrained baseline) .. 1.0 (oracle); trainable
        "dim": 16,               # embedding / latent dimension
        "grid_w": 40,            # rendered deck grid width (cells)
        "grid_h": 24,            # rendered deck grid height (cells)
    },
    "world": {
        "n_decks": 20,           # deterministic outline corpus size
        "repair_rounds": 2,      # repair harness loop rounds
    },
    "bench": {
        "skills": [0.0, 0.25, 0.5, 0.75, 1.0],
    },
    "report": {
        "format": "markdown",    # markdown | json
        "out_dir": "reports",
    },
}


def _merge(base, override):
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(recipe_path=None):
    """Return the merged config dict. A recipe (yaml subset) overrides defaults."""
    cfg = copy.deepcopy(DEFAULTS)
    if recipe_path:
        with open(recipe_path, "r", encoding="utf-8") as f:
            raw = yaml_loads(f.read())
        cfg = _merge(cfg, raw)
    return cfg
