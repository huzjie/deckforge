# -*- coding: utf-8 -*-
"""HTTP API demo using stdlib urllib (no requests needed).

Start the server first:
    python -m deckforge.cli serve --port 8431
Then run this script.
"""
import json
import os
import sys
from urllib.request import urlopen, Request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = "http://127.0.0.1:8431"


def get(path):
    with urlopen(BASE + path, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def post(path, data):
    req = Request(BASE + path, data=json.dumps(data).encode("utf-8"),
                  headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    print("health:", get("/health"))
    info = get("/v1/info")
    print("info name=%s templates=%s" % (info["name"], info["templates"]))
    deck = get("/v1/deck?template=pitch&seed=demo")
    print("deck template=%s elements=%d" % (deck["template"], len(deck["elements"])))
    run = post("/v1/run", {"deck_id": "d00", "skill": 1.0})
    print("run success=%s" % run["success"])


if __name__ == "__main__":
    main()
