# Examples

Each script is self-contained (it bootstraps `sys.path` so it can be run
directly with `python examples/<name>.py` from the project root).

| Script | What it shows |
|---|---|
| `render_deck.py` | Deterministic synthetic deck rendering as a text grid |
| `layout_element.py` | Locating a deck element from an outline point (refer) |
| `run_deck.py` | Closed-loop deck generation trace |
| `skill_curve.py` | Four skill-driven metric curves (text, no plotting lib) |
| `repair_deck.py` | Detect → locate → patch → revalidate repair harness |
| `http_api.py` | Zero-dependency HTTP API demo (needs `serve` running) |

Run them from the project root:

```bash
python examples/render_deck.py
python examples/layout_element.py
python examples/run_deck.py
python examples/skill_curve.py
python examples/repair_deck.py

# HTTP demo:
python -m deckforge.cli serve --port 8431 &   # in one terminal
python examples/http_api.py                    # in another
```
