# Course assignment mode

Use this workflow for an assignment inside an existing long-term course workspace. Reuse the single-task research, planning, drafting, and review pipeline after loading course context.

## Contents

- New-conversation intake
- Assignment workspace and context loading
- Source roles and slide policy
- Execution and required configuration

## New-conversation intake

1. Verify `workspace_mode == "course"`.
2. Read the course catalog and show concise choices when multiple courses exist.
3. Ask the user to identify the course. If only one course exists, propose it and require confirmation before saving files.
4. Read the current message and uploaded brief files using `task-intake.md`; ask for a prompt or path only when none is available.
5. Ask the user to select exactly one source scope when it cannot be inferred:
   - `course_only`: use eligible course readings; do not perform external literature retrieval;
   - `external_only`: use external literature; use course files only to interpret the brief, rubric, terminology, and instructor expectations;
   - `mixed`: use eligible course readings and external literature.
6. When the scope includes external evidence, ask for `external_access`: `institutional_library`, `public_sources`, or `both`; allow `none` when existing external files are sufficient.
7. Resolve global, course, and task preferences using `user-preferences.md`. If the course preference file is absent on the first assignment, ask whether to inherit global preferences or create a course preference.
8. Collect or locate the output type, language, word count, deadline, citation style, rubric, required sources, prohibited sources, and user's existing position.
9. Stop at the dependency gate when a classroom-only topic, group allocation, role, data set, or required draft is missing.
10. Record all selections in `assignment_config.json`.

## Assignment workspace

Create a stable assignment directory under the selected course:

```text
03_assignments/<assignment-id>/
  assignment_config.json
  00_brief/
  01_course_context/
  02_external_sources/
  03_source_registry/
  04_evidence/
  05_content_plan/
  06_draft/
  07_review/
  08_final_internal/
  <assignment-name>_result/       # create only after format confirmation
  task_summary.md
```

Store links or a selection manifest in `01_course_context/`; do not duplicate the entire course repository.

## Context loading

Load in this order and stop when sufficient:

1. current assignment request and brief;
2. selected course manifest;
3. rubric and instructor requirements;
4. `course_memory.md` and `task_index.csv`;
5. relevant prior task summaries;
6. specific prior artifacts only when directly relevant.

Do not import prior conclusions without rechecking their evidence and relevance to the current assignment.

## Source roles

Assign every candidate source a machine-readable role and citation status.

```json
{
  "origin": "course_lms",
  "material_type": "lecture_slides",
  "source_role": "context_only",
  "citation_eligibility": "prohibited"
}
```

Use these defaults:

| Material | `source_role` | `citation_eligibility` |
| --- | --- | --- |
| PPT, PPTX, or PDF exported from slides | `context_only` | `prohibited` by default |
| Assignment brief or rubric | `task_constraint` | `not_academic_evidence` |
| Syllabus | `course_constraint` | `not_academic_evidence` |
| Journal article or book chapter | `evidence` | `requires_verification` |
| Official report | `evidence` | `requires_verification` |
| Instructor handout | `context` | `conditional` |
| Discussion post or informal LMS page | `context` | `prohibited` |

Preserve original material type after conversion. A slide deck exported to PDF remains `lecture_slides` and remains subject to the same default prohibition or recorded exception.

## Slide policy

By default, use course slides only to understand concepts, terminology, course organization, instructor emphasis, and search leads. Under the default policy, never:

- cite slides in text, notes, or the reference list;
- use slides as the sole evidence for a substantive claim;
- enter slides into the citation ledger as an eligible source;
- convert slides to another format to evade the restriction.

When slides mention an original publication, prefer retrieving and verifying that publication before citing it.

The user may enable formal slide citation for the current task or a named course only by explicitly confirming that the assignment or instructor allows it. Record `slide_citation_policy: allowed_by_user_confirmation`, `slide_permission_scope`, and `slide_permission_basis`. Reject the override when a higher-priority brief or rubric conflicts. A global preference alone is insufficient.

Even with permission, a specific slide stays `requires_verification` until its authorship, title, date, course or container, access context, and relevant locator can be represented in the selected citation style. Only then may the source registry mark it `allowed`. Slides must not be the sole support for a substantive claim when a more authoritative original source is required by the task.

If `source_scope == "course_only"` and the available course files contain no sufficient citation-eligible evidence, stop before drafting. Ask the user to switch to `mixed` so original sources named in course materials can be retrieved, supply additional course readings, or confirm that the assignment requires no formal academic references. Update `assignment_config.json` after the user changes the source scope.

## Execution

1. Check the selected course's last sync status and missing-material report.
2. Ask whether to resync only when stale or missing material may affect the task.
3. Select relevant course materials according to `source_scope`.
4. Retrieve external literature only for `external_only` or `mixed`.
5. Verify source identity and citation eligibility.
6. Build the source registry, citation ledger, and evidence matrix.
7. Create a Markdown content plan and obtain the required approval.
8. Draft the complete artifact using only citation-eligible evidence.
9. Review against the brief, rubric, evidence matrix, citation style, and source policy.
10. Run a slide citation gate before final delivery. Fail when a cited slide lacks recorded permission, verified metadata, an allowed registry status, or conflicts with the brief.
11. Save approved content internally, ask for Word, PDF, or both, create the task result folder, render and verify the selected output, and write `task_summary.md`.
12. Append the task status and paths to `04_course_memory/task_index.csv`; update `04_course_memory/course_memory.md` with reusable requirements and decisions, not the full draft. Create these paths when an older or partial course workspace lacks them; do not place the task index at the course root.

## Required assignment configuration

Include at least:

```json
{
  "course_id": "course-001",
  "course_name": "Displayed course name",
  "source_scope": "mixed",
  "citation_style": "APA-7",
  "language": "English",
  "course_sync_checked": true,
  "slide_citation_policy": "prohibited",
  "slide_permission_scope": null,
  "slide_permission_basis": null,
  "external_access": "both"
}
```
