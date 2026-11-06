# Getting Started

`deckforge` is a **zero-dependency, pure-Python reference implementation** of a
slide-deck generation agent, inspired by IBM Palette's design: separate **design
and coding stages**, **synthetic training data**, and a **checked repair
harness**.

It needs only the Python standard library — no numpy / torch / requests.

## Install & run

```bash
git clone https://github.com/huzjie/deckforge.git
cd deckforge
python -m deckforge.cli doctor     # sanity: oracle reproduced at skill=1.0
python -m deckforge.cli bench      # four monotone metric curves + repair gain
python -m deckforge.cli run --deck d00 --skill 1.0
python -m deckforge.cli repair --n 8
python -m deckforge.cli serve --port 8431   # zero-dependency HTTP API
```

Or with the provided Makefile:

```bash
make test      # 47 unit tests
make bench
make doctor
```

## What it demonstrates

| Capability | Metric | Skill 0.0 → 1.0 (measured) |
|---|---|---|
| Layout placement | `layout_acc` | 0.09 → 1.00 |
| Design spec | `design_acc` | 0.04 → 1.00 |
| Closed-loop completion | `deck_success` | 0.00 → 1.00 |
| Verifiable reward | `score` | 0.01 → 1.00 |
| Checked repair | `repair_gain` | 1.00 (all broken decks fixed) |

All four metrics are **monotone by construction** (a threshold-flip drives the
skill axis), which is the property a verifiable-reward training loop needs.

## Project layout

```
deckforge/
  core/        deck renderer, elements, embed, layout, designer, engine
  world/       design oracle + deterministic corpus (synthetic data)
  training/    verifier (verifiable reward), repair harness, skill trainer
  serving/     zero-dependency HTTP API
  tasks/       declarative capability registry
  utils/       deterministic rng, minimal yaml, linear algebra
tests/         47 unit tests
prompts/       reusable prompt templates (design / layout / repair / guard / reward)
recipes/       yaml config overrides (benchmark / full / minimal / layout / design)
examples/      runnable scripts
deploy/        Docker, docker-compose, Kubernetes, Helm
docs/          this documentation
```

## Quick tour

1. `deckforge.core.deck` renders a deterministic synthetic slide into a text grid.
2. `deckforge.world.oracle` is the closed-form ground truth (single source of truth).
3. `deckforge.core.engine` flips between an untrained baseline and the oracle via
   per-item thresholds, so every metric rises monotonically in `skill`.
4. `deckforge.training.verifier` turns each element into a binary reward.
5. `deckforge.training.repair` detects / locates / patches / revalidates layout
   defects in a closed loop.
