# -*- coding: utf-8 -*-
"""Wire everything into a ready-to-use kit (corpus + oracle + engine + verifier + repairer)."""
from __future__ import annotations

from .world.corpus import build_corpus
from .world.oracle import DesignWorld
from .core.engine import Engine
from .core.embed import encode_deck
from .training.verifier import Verifier
from .training.repair import Repairer


def build_kit(cfg):
    corpus = build_corpus(cfg)
    world = DesignWorld()
    dim = cfg["model"]["dim"]
    engine = Engine(world, corpus, dim, cfg["model"]["grid_w"], cfg["model"]["grid_h"])
    verifier = Verifier(engine, world)
    repairer = Repairer(world)
    return {
        "cfg": cfg,
        "corpus": corpus,
        "world": world,
        "engine": engine,
        "verifier": verifier,
        "repairer": repairer,
        "encode_deck": lambda deck: encode_deck(deck, dim),
    }
