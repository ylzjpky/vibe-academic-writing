# Source Usage Policy

Apply this policy before planning, drafting, and final delivery. Treat file format and source identity as separate fields: a slide deck exported to PDF remains a slide deck.

## Source roles

Assign every item exactly one `source_role` and one `citation_eligibility` in the source registry.

| Material | Default role | Default eligibility |
|---|---|---|
| Peer-reviewed article, scholarly book/chapter | evidence | requires_verification |
| Government, intergovernmental, standards, or reputable institutional report | evidence | requires_verification |
| Course-assigned scholarly reading | evidence | requires_verification |
| Instructor handout or unpublished course note | context | conditional |
| Syllabus, assignment brief, rubric | task_constraint | not_bibliographic_evidence |
| Course web page or discussion post | context | conditional |
| PPT/PPTX, slide deck, or slides exported to PDF | context_only | prohibited by default |
| Video | excluded | prohibited |

`conditional` means permission or source identity still needs verification. It never overrides a higher-priority assignment or instructor rule.

## Default slide rule and explicit exception

- By default, never cite a PPT/PPTX, slide deck, or slide-derived PDF in prose, notes, or the reference list.
- Under the default policy, never use slides as the sole support for a substantive claim.
- Use slides only to understand course framing, terminology, or to discover an original source.
- If slides mention a publication, retrieve and verify that publication independently before citing it.
- Preserve `original_material_type: lecture_slides` after conversion or renaming so permission checks cannot be bypassed by changing the extension.
- If the user selects course-only sources and only prohibited slides support the requested argument, block drafting and offer: switch to mixed sources so the originals can be retrieved, add eligible readings, confirm an assignment/instructor slide permission, or proceed without citations only when the assignment permits it.

Formal slide citation is allowed only when all conditions hold:

1. the user explicitly confirms that the assignment or instructor permits it;
2. the permission scope is the current task or named course and its basis is recorded;
3. no brief, rubric, instructor rule, or integrity boundary conflicts;
4. the specific slide's authorship, title, date, course/container, access context, and locator are verified sufficiently for the selected style;
5. the normalized source registry marks it `citation_eligibility: allowed`.

A global preference is not permission. An allowed slide remains a lower-authority course source unless the task specifically treats it otherwise; prefer the original publication for substantive external claims.

## Source-scope behavior

- `user_materials_only`: use only eligible files or text supplied by the user; do not retrieve externally without approval.
- `course_only`: use eligible course readings and do not add external evidence. If external evidence becomes necessary, obtain approval and update the scope to `mixed`. Assignment instructions and rubrics still govern the work.
- `external_only`: use course files only to understand the assignment; use verified external sources as evidence.
- `mixed`: use verified eligible sources from both pools and record origin.

When scope includes external sources, record `external_access` independently as `institutional_library`, `public_sources`, `both`, or `none`.

## Eligibility procedure

For each candidate source:

1. Identify authorship, title, date, publisher/container, stable locator, material type, and origin.
2. Confirm the local file or page matches the claimed publication.
3. Check relevance, authority, recency where relevant, and whether the full text supports the intended claim.
4. Set `verification_status` and `citation_eligibility`; record a reason for any restriction.
5. Add only allowed sources to the evidence matrix and citation ledger.

Do not invent metadata, quotations, page numbers, DOIs, or locators. Mark unresolved fields explicitly. Prefer primary sources for empirical or legal claims and the original scholarly publication over a secondary summary.

## Claim rules

- Each externally verifiable substantive claim must map to at least one source that directly supports it.
- Quotations require an exact location and a check against the source text.
- Paraphrases must preserve the source's meaning and receive a citation when attribution is required.
- Distinguish source statements from the writer's inference. Label an inference in the evidence matrix.
- Conflicting sources must be represented rather than silently resolved by the agent.

Run the source-policy audit before plan approval and again before final delivery. Any cited prohibited source or fabricated/unverified citation is a blocking failure.
