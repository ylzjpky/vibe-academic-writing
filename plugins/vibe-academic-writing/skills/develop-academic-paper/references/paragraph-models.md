# Paragraph Models

Use these as planning heuristics, not rigid templates. Assign a model only when it clarifies the paragraph's function. A complex paragraph may combine models, and the writer may depart from a planned model when evidence or genre requires it; record material changes in the review notes.

## Selector

| Primary function | Preferred model |
|---|---|
| Advance a sequence, causal chain, or connected argument | Linked List |
| Present concentrated data, facts, or documented context | Data Stack |
| Compare positions, contradictions, or scholarly debate | Logic Fork |
| Define and operationalize a concept or framework | Definition & Expansion |

## Linked List

Use for historical development, causal reasoning, or staged argument.

1. Connect to the live question or preceding reasoning.
2. Explain the current mechanism, change, or inference with evidence.
3. End by exposing the next relevant consequence or unresolved link when useful.

Do not force a forward pointer in the final paragraph or when it makes the prose mechanical.

## Data Stack

Use for evidence-dense background or results.

1. State the analytical frame.
2. Present selected data or facts with provenance and meaningful ordering.
3. Interpret only to the degree the section's purpose requires.

Do not dump disconnected statistics. A concise synthesis is allowed when readers need it; avoid empty sentences such as “this shows the issue is important.”

## Logic Fork

Use for literature review and critical comparison.

1. Establish one position and its evidentiary basis.
2. Introduce a credible competing interpretation or counterevidence.
3. Compare assumptions, methods, scope, or implications.
4. State the justified synthesis, limitation, or research gap.

Do not manufacture balance when evidence strongly favors one conclusion.

## Definition & Expansion

Use for theory, concepts, and methodology.

1. Provide a sourced definition or define the working usage.
2. Distinguish dimensions, boundaries, or competing definitions.
3. Explain how the concept is operationalized in this task.

## Planning record

For each planned paragraph record:

```yaml
paragraph_id: p-01
purpose: one-sentence analytical job
model: linked-list|data-stack|logic-fork|definition-expansion|hybrid|none
claim_ids: [claim-01]
source_ids: [src-01]
transition_dependency: null
```

The model never overrides evidence accuracy, assignment genre, discipline conventions, or clarity. Review the paragraph for function and support, not superficial template compliance.
