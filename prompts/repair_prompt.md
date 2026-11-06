# Repair-Harness Prompt — Detect → Locate → Patch → Revalidate

You are a **checked repair harness**. Given a rendered deck, find and fix layout
defects in a closed loop, then revalidate.

## Loop

1. **Detect** — list every defect:
   - out-of-zone element (type outside its legal band);
   - pairwise bounding-box overlap.
2. **Locate** — name the offending element ids.
3. **Patch** — correct *only* vertical placement (preserve element identity and
   horizontal extent):
   - snap a misplaced `title`/`subtitle`/`caption`/`footer` back to its band;
   - re-stack overlapping content elements in their spec order inside the middle
     band.
4. **Revalidate** — confirm zero overlaps and zero out-of-zone elements.

## Why this matters

Palette reports a ~3.5-point average improvement from its repair harness on
PresentBench. The key is that every fix is *checkable*: after patching, a
program can prove the deck is valid again — no human review needed.

## Output

```yaml
report:
  out_of_zone: [subtitle, footer]
  overlaps: [[chart, bullet]]
fixed: true
```
