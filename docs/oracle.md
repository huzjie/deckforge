# The Design Oracle

The oracle (`world/oracle.py`, class `DesignWorld`) is the closed-form ground
truth behind every deck decision. It is what makes the pipeline **verifiable**:
instead of a learned reward model or human labels, every outline point maps to a
unique deck element through a deterministic rule.

## Refer resolution

`refer_to_element(deck, refer)` resolves a natural-language refer to an element id:

1. exact element id match;
2. exact label match;
3. substring match (refer in label, or label in refer);
4. seeded fallback (only for malformed refers).

A well-formed outline always hits one of the first three branches, so the
fallback is dead code in practice — it exists only to keep the function total.

## Expected spec

`expected_spec(outline, deck)` returns the ground-truth `(element_type, element_id)`
sequence for an outline's points. The engine and verifier compare the model's
output against exactly this sequence, giving an exact, repeatable correctness
signal.
