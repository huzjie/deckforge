# Contributing

Contributions are welcome. The project is deliberately zero-dependency and
deterministic — please keep both properties.

## Development loop

```bash
python -m compileall -q deckforge tests
python -m unittest discover -s tests -t .
python -m deckforge.cli doctor
python -m deckforge.cli bench
```

## Conventions

1. **Zero dependencies** — stdlib only. No numpy / torch / requests in the package.
2. **Determinism** — all randomness flows through `deckforge.utils.rng` (md5-seeded).
3. **Monotone benchmarks** — new metrics must stay non-decreasing in `skill`; the
   baseline must be an independent coin-flip, never an anti-oracle.
4. **Measured numbers** — README / docs benchmark tables come from actually running
   `bench`, never hand-written estimates.
5. **Type + target + point** — the verifier's three conditions are the contract
   every new element type must satisfy.

## Tests

Add a `tests/test_<module>.py` for each new module. Keep tests fast and
deterministic (the full suite runs in well under a second).

## Pull requests

Keep changes focused; run the full loop above before opening a PR.
