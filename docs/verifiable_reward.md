# Verifiable Reward

`deckforge` produces a **binary, program-checkable reward** — the "可验证奖励"
idea, made concrete for deck generation.

## Per-element check

An element earns reward `1.0` only if **all three** conditions hold:

1. **type_ok** — emitted `element_type` equals the oracle's expected type;
2. **target_ok** — emitted `target_element` equals the oracle's expected element;
3. **point_ok** — the emitted bbox point lands inside the expected element's box.

Any element the verifier cannot confirm earns `0` — this is what suppresses
"hallucinated" elements (targeting an element the outline never asked for).

## Deck-level checks

For the full deck score we additionally require **layout validity** (zero
overlaps, zero out-of-zone elements) and **content completeness** (every outline
point covered exactly once).

## Why it is monotone

The engine flips each point from an independent baseline to the oracle via a
per-item threshold. As `skill` rises, more points flip, so the mean reward is
non-decreasing by construction — exactly the property a verifiable-reward
training loop (see `training/trainer.py`) needs.
