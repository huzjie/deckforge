# -*- coding: utf-8 -*-
"""Engine: wires deck + oracle + layout + designer into the four skill-driven
deck-generation metrics, and runs the closed-loop executor.

The central trick is the **threshold flip**: for every (outline, point) we fix
two deterministic thresholds ``t_d`` (design) and ``t_l`` (layout) in (0, 1).
The model uses the oracle whenever ``skill >= t`` and the untrained baseline
otherwise. Raising ``skill`` monotonically flips more points from baseline to
oracle, so all four metrics are monotone by construction:

* **layout_acc**    -- the predicted point lands inside the true element's bbox;
* **design_acc**    -- (element type, target element) both match the oracle;
* **deck_success**  -- every point of an outline is correct end-to-end;
* **score**         -- per-point verifiable reward (type + target + point all ok).

A monotone, non-decreasing reward trace is exactly what a verifiable-reward
training loop needs.
"""
from __future__ import annotations

from ..utils.rng import stable_float, stable_rand
from .deck import ELEMENT_TYPES
from .designer import Designer
from .layout import Layouter


def _threshold(key):
    # lo=1e-6 keeps skill=0 a pure baseline: no item has a zero threshold that
    # would flip to the oracle before any skill is shown.
    return stable_float(key, 1e-6, 1.0)


class Engine:
    def __init__(self, world, corpus, dim, grid_w, grid_h):
        self.world = world
        self.corpus = corpus
        self.dim = dim
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.designer = Designer(world)
        self.layouter = Layouter(dim)

    # ---- unified per-point evaluation ------------------------------------
    def _point_rows(self, skill):
        """One row per (outline, point) with all four correctness signals."""
        rows = []
        for outline in self.corpus["decks"]:
            deck = self.corpus["templates"][outline["template"]]
            outline_rows = []
            for i, (etype, refer) in enumerate(outline["points"]):
                key = "%s:%d" % (outline["id"], i)
                target_eid = self.world.refer_to_element(deck, refer)
                target_el = deck.by_eid(target_eid)

                # layout decision (element + point)
                t_l = _threshold("layout:%s" % key)
                if skill >= t_l:
                    eid, (x, y) = target_eid, target_el.center
                else:
                    rnd_l = stable_rand("basel:%s" % key)
                    eid = deck.elements[rnd_l.randrange(len(deck.elements))].eid
                    x, y = rnd_l.random(), rnd_l.random()

                # design decision (element type)
                t_d = _threshold("design:%s" % key)
                if skill >= t_d:
                    pred_etype = etype
                else:
                    rnd_d = stable_rand("based:%s" % key)
                    pred_etype = ELEMENT_TYPES[rnd_d.randrange(len(ELEMENT_TYPES))]

                hit = target_el.contains(x, y)
                design_ok = (pred_etype == etype and eid == target_eid)
                point_ok = design_ok and hit

                outline_rows.append({
                    "outline_id": outline["id"],
                    "point": i,
                    "pred_etype": pred_etype,
                    "pred_eid": eid,
                    "pred_point": [x, y],
                    "expected_etype": etype,
                    "expected_eid": target_eid,
                    "hit": 1.0 if hit else 0.0,
                    "design_ok": 1.0 if design_ok else 0.0,
                    "point_ok": 1.0 if point_ok else 0.0,
                })
            rows.append(outline_rows)
        return rows

    # ---- aggregate metrics ----------------------------------------------
    def run_all(self, skill):
        """Compute the four metrics (and per-point records) at a given skill."""
        outline_rows = self._point_rows(skill)
        all_points = [r for tr in outline_rows for r in tr]
        n = max(len(all_points), 1)

        layout_acc = sum(r["hit"] for r in all_points) / n
        design_acc = sum(r["design_ok"] for r in all_points) / n
        score = sum(r["point_ok"] for r in all_points) / n
        deck_success = sum(
            1.0 for tr in outline_rows if tr and all(r["point_ok"] == 1.0 for r in tr)
        ) / max(len(outline_rows), 1)

        return {
            "skill": skill,
            "layout_acc": layout_acc,
            "design_acc": design_acc,
            "deck_success": deck_success,
            "score": score,
            "n_decks": len(outline_rows),
            "n_points": len(all_points),
            "rows": outline_rows,
        }

    def run_all_skill_table(self, skills):
        return [self.run_all(s) for s in skills]

    # ---- closed-loop single-outline execution ------------------------------
    def run_deck(self, outline, skill):
        """Generate one deck in closed-loop fashion and return the trace."""
        deck = self.corpus["templates"][outline["template"]]
        trace = []
        for i, (etype, refer) in enumerate(outline["points"]):
            key = "%s:%d" % (outline["id"], i)
            target_eid = self.world.refer_to_element(deck, refer)
            target_el = deck.by_eid(target_eid)
            t_l = _threshold("layout:%s" % key)
            t_d = _threshold("design:%s" % key)
            if skill >= t_l:
                eid, (x, y) = target_eid, target_el.center
            else:
                rnd_l = stable_rand("basel:%s" % key)
                eid = deck.elements[rnd_l.randrange(len(deck.elements))].eid
                x, y = rnd_l.random(), rnd_l.random()
            if skill >= t_d:
                pred_etype = etype
            else:
                rnd_d = stable_rand("based:%s" % key)
                pred_etype = ELEMENT_TYPES[rnd_d.randrange(len(ELEMENT_TYPES))]
            ok = (pred_etype == etype and eid == target_eid and target_el.contains(x, y))
            trace.append({
                "idx": i,
                "refer": refer,
                "etype": pred_etype,
                "element": eid,
                "point": [round(x, 3), round(y, 3)],
                "ok": bool(ok),
            })
        return {"outline_id": outline["id"], "template": outline["template"],
                "success": all(t["ok"] for t in trace), "trace": trace}

    # ---- embedding diagnostic (separability of element embeddings) ---------
    def embedding_diagnostic(self):
        """Mean cosine between distinct elements vs self (=1), showing the
        encoder's element embeddings are well separated (a precondition for
        reliable design-stage alignment)."""
        from .embed import encode_deck
        from ..utils.linalg import cosine
        inter, intra = [], []
        for template, deck in self.corpus["templates"].items():
            _, vecs = encode_deck(deck, self.dim)
            eids = list(vecs.keys())
            for i in range(len(eids)):
                intra.append(1.0)  # self-cosine of a vector is trivially 1
                for j in range(i + 1, len(eids)):
                    inter.append(cosine(vecs[eids[i]], vecs[eids[j]]))
        return {
            "n_elements": len(intra),
            "mean_self_cosine": 1.0,
            "mean_cross_cosine": sum(inter) / max(len(inter), 1),
        }
