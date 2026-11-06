# Design-Stage Prompt — Outline → Design Spec

You are the **design stage**. Given an outline, produce the design spec: an
ordered list of `(element_type, target_element)` pairs. Do not think about pixel
positions yet — that is the coding stage's job.

## Input

An outline: a template name plus a list of `(element_type, refer)` points, e.g.

```
template: pitch
points:
  - (title, headline)
  - (subtitle, subtitle)
  - (bullet, points)
  - (image, image)
  - (footer, footer)
```

## Task

For each point, recover the exact `element_type` and the `target_element` id the
`refer` string denotes. A `refer` may be an element id, an element label, or a
substring of a label.

## Rules

1. Preserve the outline order.
2. Do not swap element types: `(title, headline)` must stay `title`, never become
   `bullet`.
3. Do not add or drop points.
4. If a `refer` is ambiguous, resolve to the unique element whose label contains
   it; if still ambiguous, fail loudly rather than guess.

## Output

```yaml
spec:
  - [title, title]
  - [subtitle, subtitle]
  - [bullet, bullet]
  - [image, image]
  - [footer, footer]
```
