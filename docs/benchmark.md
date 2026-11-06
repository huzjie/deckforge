# Benchmark

`python -m deckforge.cli bench` sweeps `skill` over `[0.0, 0.25, 0.5, 0.75, 1.0]`
and reports four metrics plus the repair gain. All numbers below are **measured**
on the default config (`dim=16`, `grid=40x24`, `n_decks=20`).

## Skill table

| skill | layout_acc | design_acc | deck_success | score |
|---|---|---|---|---|
| 0.00 | 0.0900 | 0.0400 | 0.0000 | 0.0100 |
| 0.25 | 0.2900 | 0.1400 | 0.0000 | 0.0800 |
| 0.50 | 0.5400 | 0.3200 | 0.0000 | 0.2400 |
| 0.75 | 0.7800 | 0.5600 | 0.0000 | 0.5200 |
| 1.00 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Monotonicity

All four metrics are non-decreasing across the skill axis (`layout_acc_inc`,
`design_acc_inc`, `deck_success_inc`, `score_inc` all `True`), by construction of
the threshold flip.

## Repair gain

Over 8 deterministically broken decks (vertical band jitter), the repair harness
fixes **all** of them (`broken=8 fixed=8 after=0 gain=1.0000`). The gain is exact
and repeatable because the patch is deterministic.

## Notes

- The untrained baseline (`skill=0.0`) is an *independent coin-flip*, not an
  anti-oracle, so its metrics sit near chance rather than zero.
- `deck_success` stays `0` until `skill=1.0` because every point of a deck must
  be correct for the deck to count as successful (a strict all-or-nothing metric).
