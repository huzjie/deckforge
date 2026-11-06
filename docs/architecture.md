# Architecture

The pipeline mirrors IBM Palette's **separate design and coding stages**, with a
closed-form oracle and a checked repair harness on top.

```
Outline (semantic points)
        │
        ▼
┌─────────────────┐   design spec   ┌──────────────────┐
│  Design stage   │ ──────────────► │   Coding stage   │
│ (designer.py)   │  (type, target) │   (layout.py)    │
└─────────────────┘                 └──────────────────┘
        │                                   │
        │                          bbox + text grid
        ▼                                   ▼
┌────────────────────────────────────────────────────┐
│              Closed-form Design Oracle             │  (world/oracle.py)
│        single source of ground truth               │
└────────────────────────────────────────────────────┘
        │                                   │
        ▼                                   ▼
┌──────────────────┐              ┌───────────────────┐
│ Verifiable reward│              │   Repair harness  │
│ (training/       │              │  (training/       │
│  verifier.py)    │              │   repair.py)      │
└──────────────────┘              └───────────────────┘
```

## Components

### 1. Synthetic deck renderer (`core/deck.py`)

Instead of pixels, a slide is rendered into a deterministic **text grid**. Each
element (`title` / `bullet` / `chart` / `image` / `footer` …) occupies a
normalized bounding box. Given a template name + seed, the same deck reproduces
bit-for-bit — the precondition for a verifiable reward.

### 2. Semantic encoder (`core/embed.py`)

Every element gets a deterministic embedding from its `(type, label)`. An outline
point's refer string is aligned to the right element in the same vector space
(no training-time alignment table). At `skill=1.0` the alignment is exact; at
`skill=0.0` it is pure noise.

### 3. Layout + design heads (`core/layout.py`, `core/designer.py`)

- **Layout** (coding stage) returns an element + bbox point for a refer.
- **Design** (design stage) returns `(element_type, target_element)` per point.

### 4. Engine (`core/engine.py`)

The central trick is the **threshold flip**: for every `(outline, point)` we fix
two thresholds `t_l` (layout) and `t_d` (design) in `(0,1)`. When `skill >= t` the
model uses the oracle; otherwise it uses an *independent coin-flip* baseline.
Raising `skill` monotonically flips more points from baseline to oracle, so all
four metrics are monotone by construction.

### 5. Repair harness (`training/repair.py`)

Detect (overlap / out-of-zone) → locate (offending ids) → patch (zone snap +
deterministic re-stack, preserving element identity and horizontal extent) →
revalidate. Fully deterministic, so "repair gain" is exact and repeatable.

### 6. Verifier + trainer (`training/verifier.py`, `training/trainer.py`)

A binary reward (type + target + point all match), and a monotone skill axis whose
update is always non-negative.
