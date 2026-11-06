# Synthetic Deck Rendering

`deckforge` renders a slide as a **deterministic text grid** — a zero-dependency
stand-in for a real presentation engine. This is the "coding stage" observation:
the design stage emits an element spec, and the coding stage materializes it into
a checkable layout.

## Element vocabulary

`title` `subtitle` `bullet` `image` `chart` `table` `code` `footer` `caption`

## Templates

Five deterministic templates, each a fixed element list:

| template | elements |
|---|---|
| `pitch` | title, subtitle, bullet, image, footer |
| `report` | title, chart, bullet, table, footer |
| `tutorial` | title, subtitle, code, caption, footer |
| `metrics` | title, chart, chart, caption, footer |
| `roadmap` | title, bullet, bullet, image, footer |

## Layout zones

Each element type is legal only inside its vertical band (normalized y):

| type | band |
|---|---|
| title | 0.00 – 0.17 |
| subtitle | 0.18 – 0.28 |
| bullet / image / chart / table / code | 0.30 – 0.76 |
| caption | 0.77 – 0.85 |
| footer | 0.86 – 1.00 |

The bands are disjoint with clear gaps, so a repair snap always lands in a
non-overlapping position.

## Determinism

The layout derives from `md5("<template>:<seed>:layout")` via `utils.rng.stable_rand`.
The same `(template, seed)` always reproduces the same bboxes and the same grid —
which is what lets two independent runs of an outline see identical ground truth.
