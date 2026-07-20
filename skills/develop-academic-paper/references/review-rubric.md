# Review Rubric and Delivery Gates

The reviewer evaluates the complete artifact against the assignment, approved plan, source registry, and citation configuration. Report evidence for each result. A high prose score cannot override a blocking gate.

## Blocking gates

Final delivery is blocked if any condition is true:

1. Course, assignment, source scope, or required citation style is unresolved.
2. The content plan has not been approved by the user.
3. A cited source is `prohibited` or unverified; a cited slide also lacks a recorded task/course permission, complete verified metadata, or an `allowed` registry status.
4. A quotation, factual claim, statistic, or attribution is fabricated or not supported by the cited source.
5. A citation does not resolve to the source registry, or required bibliography/note coverage is materially incomplete.
6. Required assignment sections, word constraints, rubric criteria, or explicit instructor rules are materially unmet.
7. A downloaded file used as evidence is corrupt, mismatched, or incomplete.
8. The final validation scripts report a blocking error.

## Scored review

Rate each dimension `pass`, `revise`, or `fail` and cite the affected artifact IDs.

| Dimension | Pass standard |
|---|---|
| Task compliance | Answers the actual prompt, genre, language, length, and rubric requirements |
| Thesis and reasoning | Central claim is clear; reasoning is coherent; conclusions match evidence |
| Evidence quality | Sources are relevant, authoritative, sufficiently varied, and directly supportive |
| Source fidelity | Paraphrases, quotations, data, limitations, and disagreements reflect source meaning |
| Structure | Sections and paragraphs have purposeful progression; models support rather than constrain clarity |
| Critical engagement | Alternatives, limits, and counterevidence are addressed at the level the task requires |
| Citation correctness | In-text citations/notes and bibliography follow the configured style consistently |
| Academic style | Prose is precise, readable, appropriately formal, and free of empty signposting or unsupported certainty |
| Artifact integrity | Required configs, registry, ledger, plan, review, final files, and paths are consistent |

## Review procedure

1. Re-read the task brief, rubric, instructor requirements, and approved plan.
2. Run source-policy and citation audits before stylistic editing.
3. Sample-check every quotation and all high-risk claims; check all citations when feasible.
4. Compare section and paragraph purposes against the evidence matrix.
5. Check the configured citation style, including notes/bibliography behavior and institutional Harvard/custom rules.
6. Run artifact validation and verify final paths.
7. Classify findings as `blocking`, `required_revision`, or `optional`.
8. After revision, rerun affected gates; do not carry forward an old pass automatically.

## Final validation report

Write `validation_report.md` with:

```yaml
overall_status: pass|blocked
task_compliance: pass|revise|fail
source_policy: pass|fail
citation_integrity: pass|fail
artifact_integrity: pass|fail
blocking_issue_count: 0
required_revision_count: 0
checked_at: ISO-8601
```

List checked files and commands, then unresolved limitations. Delivery is allowed only when `overall_status: pass`; optional refinements may remain if they do not affect correctness or task compliance.
