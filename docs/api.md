# HTTP API

`deckforge` ships a zero-dependency HTTP API on the stdlib `http.server`
(`deckforge/serving/app.py`).

## Start

```bash
python -m deckforge.cli serve --host 127.0.0.1 --port 8431
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` |
| GET | `/v1/info` | model + task metadata |
| GET | `/v1/deck?template=&seed=` | render a synthetic deck |
| POST | `/v1/layout` | locate an element for a refer (`?skill=`) |
| POST | `/v1/design` | design an outline into an element spec |
| POST | `/v1/run` | closed-loop generation trace |
| POST | `/v1/repair` | repair a broken deck and report |

## Examples

```bash
curl "http://127.0.0.1:8431/health"
curl "http://127.0.0.1:8431/v1/deck?template=pitch&seed=demo"

curl -X POST http://127.0.0.1:8431/v1/run \
  -H "Content-Type: application/json" \
  -d '{"deck_id": "d00", "skill": 1.0}'
```

See `examples/http_api.py` for a stdlib-urllib client.
