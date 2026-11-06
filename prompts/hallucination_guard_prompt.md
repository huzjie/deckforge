# Hallucination-Guard Prompt

A slide-deck agent's most damaging failure is a **hallucinated element**: placing
a `chart` the outline never asked for, or inventing a `footer` the template does
not contain. This prompt is a guard that runs before the design spec is emitted.

## Checks (all must pass)

1. **Closed vocabulary** — every emitted `element_type` is one of
   `title subtitle bullet image chart table code footer caption`.
2. **Coverage = 1:1** — the number of emitted elements equals the number of
   outline points; no extra, no missing.
3. **Type fidelity** — an outline point of type `title` must be emitted as
   `title`, never silently "upgraded" or "downgraded".
4. **Target existence** — every `target_element` id/label exists in the deck's
   element list.

## Behavior

If any check fails, refuse to emit and return a structured error
(`{"hallucination": true, "reason": ...}`). A hallucinated element earns zero
reward under the verifiable-reward scheme, so blocking it here is strictly
better than letting it reach the layout stage.

## Output

```yaml
guard: pass
elements: 5   # == len(outline.points)
phantom: []
```
