# -*- coding: utf-8 -*-
"""Test helpers: a cached kit so tests share one build."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckforge.config import load_config  # noqa: E402
from deckforge.kit import build_kit  # noqa: E402

_KIT = None


def get_kit():
    global _KIT
    if _KIT is None:
        cfg = load_config()
        _KIT = build_kit(cfg)
    return _KIT


def get_cfg():
    return load_config()
