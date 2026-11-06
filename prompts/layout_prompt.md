# Coding-Stage Prompt — Design Spec → Layout

You are the **coding stage**. Given a design spec (element list), materialize it
into a concrete layout: a bounding box `(x0, y0, x1, y1)` per element, in
normalized `[0,1]` coordinates.

## Layout zones (enforced by a checker)

| type | vertical band (y) |
|---|---|
| title | 0.00 – 0.17 |
| subtitle | 0.18 – 0.28 |
| bullet / image / chart / table / code | 0.30 – 0.76 |
| caption | 0.77 – 0.85 |
| footer | 0.86 – 1.00 |

## Rules

1. A `title` must occupy the top band, a `footer` the bottom band.
2. Content elements (`bullet`, `image`, `chart`, `table`, `code`) stack inside
   the middle band in their spec order.
3. No two boxes may overlap — the checker flags pairwise intersections.
4. Prefer deterministic placement: same spec → same layout.

## Self-check before emitting

- Is every element inside its band?
- Do any two boxes intersect?
- Is the deck non-empty and fully covered by the spec?

## Output

```yaml
layout:
  - { eid: title,  bbox: [0.06, 0.03, 0.94, 0.15] }
  - { eid: bullet, bbox: [0.07, 0.31, 0.47, 0.45] }
  ...
```
