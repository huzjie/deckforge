# Verifiable-Reward Prompt

You convert a generated deck into a **binary, program-checkable reward** — no
learned reward model, no human labels.

## Per-element check (reward = 1.0 only if ALL three hold)

1. **type_ok** — emitted `element_type` equals the oracle's expected type;
2. **target_ok** — emitted `target_element` equals the oracle's expected element;
3. **point_ok** — the emitted bbox point lands inside the expected element's
   bounding box.

## Deck-level checks (for the full score)

- **layout validity** — zero overlaps, zero out-of-zone elements;
- **content completeness** — every outline point is covered exactly once.

## Why this is "verifiable"

Each condition is a deterministic rule over a closed-form layout model. Two
independent runs of the same outline therefore see the same ground truth and the
same reward — which is what lets a training loop climb the reward trace
monotonically (see `deckforge.training.trainer`).

## Output

```yaml
reward: 1.0
checks:
  type_ok: true
  target_ok: true
  point_ok: true
```
