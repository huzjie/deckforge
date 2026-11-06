# -*- coding: utf-8 -*-
"""Command-line interface: doctor / bench / modes / run / train / repair / serve."""
from __future__ import annotations

import argparse
import json

from .config import load_config
from .kit import build_kit
from . import bench as benchmod
from .training.trainer import RewardTrainer
from .tasks import list_tasks


def cmd_doctor(cfg):
    kit = build_kit(cfg)
    engine = kit["engine"]
    r = engine.run_all(1.0)
    diag = engine.embedding_diagnostic()
    print("[doctor] templates=%s decks=%d points=%d dim=%d grid=%dx%d"
          % (",".join(sorted(kit["corpus"]["templates"].keys())),
             r["n_decks"], r["n_points"], cfg["model"]["dim"],
             cfg["model"]["grid_w"], cfg["model"]["grid_h"]))
    print("[doctor] layout_acc=%.4f design_acc=%.4f deck_success=%.4f score=%.4f"
          % (r["layout_acc"], r["design_acc"], r["deck_success"], r["score"]))
    print("[doctor] embedding separability: mean_cross_cosine=%.4f (elements=%d)"
          % (diag["mean_cross_cosine"], diag["n_elements"]))
    ok = (r["layout_acc"] >= 0.9999 and r["design_acc"] >= 0.9999
          and r["deck_success"] >= 0.9999 and r["score"] >= 0.9999)
    if not ok:
        raise SystemExit("[doctor] FAIL: metrics not at oracle level at skill=1.0")
    print("[doctor] OK (oracle reproduced across all four capabilities at skill=1.0)")


def cmd_bench(cfg):
    table = benchmod.run_skill_table(cfg)
    print("[bench] skill  layout_acc  design_acc  deck_success  score")
    for r in table:
        print("[bench] %.2f   %.4f       %.4f       %.4f         %.4f"
              % (r["skill"], r["layout_acc"], r["design_acc"],
                 r["deck_success"], r["score"]))
    s = benchmod.summarize(table)
    print("[bench] layout %.4f->%.4f | design %.4f->%.4f | deck_success %.4f->%.4f | score %.4f->%.4f"
          % (s["layout_acc"][0], s["layout_acc"][1],
             s["design_acc"][0], s["design_acc"][1],
             s["deck_success"][0], s["deck_success"][1],
             s["score"][0], s["score"][1]))
    mono = benchmod.check_monotone(table)
    print("[bench] monotone: %s" % ", ".join("%s=%s" % (k, v) for k, v in mono.items()))
    rg = benchmod.run_repair_gain(cfg)
    print("[bench] repair_gain: broken=%d fixed=%d after=%d gain=%.4f"
          % (rg["broken_before"], rg["fixed"], rg["broken_after"], rg["gain"]))


def cmd_modes(cfg):
    kit = build_kit(cfg)
    corpus = kit["corpus"]
    print("[modes] templates=%s" % ", ".join(sorted(corpus["templates"].keys())))
    print("[modes] decks=%d points/deck=%d" % (len(corpus["decks"]),
          len(corpus["decks"][0]["points"])))
    print("[modes] capabilities=%s" % ", ".join(t["id"] for t in list_tasks()))
    print("[modes] dim=%d grid=%dx%d skill=%.2f"
          % (cfg["model"]["dim"], cfg["model"]["grid_w"], cfg["model"]["grid_h"],
             cfg["model"]["skill"]))


def cmd_run(cfg, args):
    kit = build_kit(cfg)
    corpus = kit["corpus"]
    engine = kit["engine"]
    outline = next((d for d in corpus["decks"] if d["id"] == args.deck), None)
    if outline is None:
        outline = corpus["decks"][0]
        print("[run] unknown deck; using %s" % outline["id"])
    res = engine.run_deck(outline, args.skill)
    print("[run] deck=%s template=%s success=%s"
          % (outline["id"], outline["template"], res["success"]))
    for tr in res["trace"]:
        mark = "OK" if tr["ok"] else "!!"
        print("[run]   point %d [%s] %s -> %s @ (%s,%s)"
              % (tr["idx"], mark, tr["etype"], tr["element"],
                 tr["point"][0], tr["point"][1]))


def cmd_train(cfg, args):
    kit = build_kit(cfg)
    trainer = RewardTrainer(kit["verifier"], skill=args.start, lr=args.lr)
    for i in range(args.steps):
        rec = trainer.step()
        print("[train] step %02d skill=%.4f score=%.4f delta=%.4f"
              % (rec["step"], rec["skill"], rec["reward"], rec["delta"]))
    print("[train] score monotone=%s" % trainer.is_monotone())


def cmd_repair(cfg, args):
    from .bench import run_repair_gain
    rg = run_repair_gain(cfg, n=args.n)
    print("[repair] broken=%d fixed=%d after=%d gain=%.4f"
          % (rg["broken_before"], rg["fixed"], rg["broken_after"], rg["gain"]))


def cmd_serve(cfg, args):
    from .serving.app import serve
    serve(host=args.host, port=args.port, cfg=cfg)


def build_parser():
    ap = argparse.ArgumentParser(
        prog="deckforge",
        description="Slide-deck generation agent (Palette-style) reference implementation")
    ap.add_argument("--recipe", default=None, help="yaml recipe to merge over defaults")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("doctor")
    sub.add_parser("bench")
    sub.add_parser("modes")

    p = sub.add_parser("run")
    p.add_argument("--deck", default=None)
    p.add_argument("--skill", type=float, default=1.0)

    p = sub.add_parser("train")
    p.add_argument("--steps", type=int, default=10)
    p.add_argument("--lr", type=float, default=0.05)
    p.add_argument("--start", type=float, default=0.0)

    p = sub.add_parser("repair")
    p.add_argument("--n", type=int, default=8)

    p = sub.add_parser("serve")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8431)
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    cfg = load_config(args.recipe)
    if args.cmd is None:
        ap.print_help()
        return

    dispatch = {
        "doctor": lambda: cmd_doctor(cfg),
        "bench": lambda: cmd_bench(cfg),
        "modes": lambda: cmd_modes(cfg),
        "run": lambda: cmd_run(cfg, args),
        "train": lambda: cmd_train(cfg, args),
        "repair": lambda: cmd_repair(cfg, args),
        "serve": lambda: cmd_serve(cfg, args),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
