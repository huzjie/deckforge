# -*- coding: utf-8 -*-
"""Zero-dependency HTTP API (stdlib http.server) over the deck pipeline.

Endpoints:
  GET  /health            -> {"status": "ok"}
  GET  /v1/info           -> model + task metadata
  GET  /v1/deck           -> render a synthetic deck (?template=&seed=)
  POST /v1/layout         -> locate an element for a refer (?skill=)
  POST /v1/design         -> design an outline into an element spec (?skill=)
  POST /v1/run            -> closed-loop generation trace for an outline (?skill=)
  POST /v1/repair         -> repair a broken deck and report the gain
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from ..kit import build_kit
from ..core.deck import render_deck
from ..training.repair import repair_elements, Repairer


def _make_handler(cfg):
    kit = build_kit(cfg)
    corpus = kit["corpus"]
    engine = kit["engine"]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # silence request logging
            pass

        def _send(self, code, obj):
            body = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _body(self):
            n = int(self.headers.get("Content-Length", 0) or 0)
            if n <= 0:
                return {}
            raw = self.rfile.read(n)
            try:
                return json.loads(raw.decode("utf-8"))
            except Exception:
                return {}

        def _query(self):
            return parse_qs(urlparse(self.path).query)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/health":
                return self._send(200, {"status": "ok"})
            if path == "/v1/info":
                return self._send(200, {
                    "name": "deckforge",
                    "version": "0.1.0",
                    "dim": cfg["model"]["dim"],
                    "grid": [cfg["model"]["grid_w"], cfg["model"]["grid_h"]],
                    "templates": sorted(corpus["templates"].keys()),
                    "decks": [d["id"] for d in corpus["decks"]],
                    "capabilities": ["layout", "design", "completion", "verifiable_reward", "repair"],
                })
            if path == "/v1/deck":
                q = self._query()
                template = q.get("template", [None])[0]
                seed = q.get("seed", ["api"])[0]
                deck = render_deck(seed=seed, template=template,
                                   grid_w=cfg["model"]["grid_w"],
                                   grid_h=cfg["model"]["grid_h"])
                return self._send(200, {
                    "template": deck.template,
                    "grid": deck.grid,
                    "elements": [
                        {"eid": e.eid, "type": e.etype, "label": e.label,
                         "bbox": list(e.bbox), "center": list(e.center)}
                        for e in deck.elements
                    ],
                })
            return self._send(404, {"error": "not found"})

        def do_POST(self):
            path = urlparse(self.path).path
            data = self._body()
            skill = float(data.get("skill", cfg["model"]["skill"]))

            if path == "/v1/layout":
                template = data.get("template", "pitch")
                refer = data.get("refer")
                if not refer:
                    return self._send(400, {"error": "missing 'refer'"})
                deck = corpus["templates"].get(template)
                if deck is None:
                    return self._send(400, {"error": "unknown template '%s'" % template})
                target_eid = kit["world"].refer_to_element(deck, refer)
                eid, (x, y) = engine.layouter.locate(deck, refer, skill, target_eid)
                return self._send(200, {"template": template, "refer": refer,
                                        "predicted_eid": eid,
                                        "point": [round(x, 3), round(y, 3)],
                                        "skill": skill})

            if path == "/v1/design":
                deck_id = data.get("deck_id")
                outline = next((d for d in corpus["decks"] if d["id"] == deck_id), None)
                if outline is None:
                    outline = corpus["decks"][0]
                deck = corpus["templates"][outline["template"]]
                spec = engine.designer.design(outline, deck, skill)
                return self._send(200, {"deck_id": outline["id"], "template": outline["template"],
                                        "spec": [list(p) for p in spec], "skill": skill})

            if path == "/v1/run":
                deck_id = data.get("deck_id")
                outline = next((d for d in corpus["decks"] if d["id"] == deck_id), None)
                if outline is None:
                    outline = corpus["decks"][0]
                result = engine.run_deck(outline, skill)
                return self._send(200, result)

            if path == "/v1/repair":
                template = data.get("template", "pitch")
                deck = render_deck(seed=data.get("seed", "broken"), template=template,
                                   grid_w=cfg["model"]["grid_w"],
                                   grid_h=cfg["model"]["grid_h"])
                from ..core.elements import count_conflicts
                before = count_conflicts(deck.elements)
                repair_elements(deck.elements, seed="api-repair")
                after = count_conflicts(deck.elements)
                return self._send(200, {"template": template,
                                        "conflicts_before": before,
                                        "conflicts_after": after,
                                        "fixed": before > 0 and after == 0})

            return self._send(404, {"error": "not found"})

    return Handler


def serve(host="127.0.0.1", port=8431, cfg=None):
    if cfg is None:
        from ..config import load_config
        cfg = load_config()
    handler = _make_handler(cfg)
    srv = ThreadingHTTPServer((host, port), handler)
    print("[serve] listening on %s:%d (Ctrl-C to stop)" % (host, port))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
