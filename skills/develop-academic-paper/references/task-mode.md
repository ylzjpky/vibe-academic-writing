# Single-task mode

Use this workflow for standalone assignments that are not attached to a long-term course. The selected workspace is a container; every new task receives a task-named child directory.

## Contents

- Intake and workspace layout
- Research, planning, drafting, and review
- Stop conditions

## Intake

1. Inspect the current directory, conversation text, and relevant uploaded files before asking questions. Follow `task-intake.md`.
2. Extract the following fields and ask only for missing or conflicting material decisions:
   - task title or prompt;
   - output type and language;
   - word count or length range;
   - deadline, if relevant;
   - citation style;
   - rubric, instructions, required sources, and prohibited sources;
   - user's thesis, position, or existing material.
3. Record unresolved nonblocking fields as `null`; do not invent institutional requirements.
4. Stop at the dependency gate when a classroom allocation, group role, required data, missing draft, or other absent fact changes the task.
5. Ask the user to confirm the interpreted assignment only when ambiguity changes research, structure, source selection, or citation behavior.
6. Run `preflight_workspace.py` on the selected container. Resolve or explicitly acknowledge any cloud-sync warning.
7. Create a sanitized `<task-name>/` child directory without overwriting existing user files.

## Workspace

Use this logical structure. Reuse compatible existing directories instead of duplicating them.

For a schema v1.0 workspace that already stores `task_config.json` at the root, continue that existing task in place. Do not move user artifacts automatically. Create all new v1.1+ tasks as named child directories.

```text
workspace-root/
  workspace_config.json
  user_preferences.md              # only after the user supplies durable preferences
  <task-name>/
    task_config.json
    00_brief/
    01_sources/
      incoming/
      verified/
      rejected/
    02_source_registry/
    03_evidence/
    04_content_plan/
    05_draft/
    06_review/
    07_final_internal/
    <task-name>_result/            # create only after format confirmation
    task_summary.md
    run_state.json
    resume_state.json
```

Keep original source files unchanged. Store derived notes separately.

## Research and source control

1. Resolve effective global and task-specific preferences using `user-preferences.md`.
2. Inventory user-provided files before searching externally.
3. Derive search questions from the assignment, not from a predetermined conclusion.
4. Separate `source_scope` from `external_access`. If external retrieval is needed, ask whether to use the institutional library, public scholarly sources, or both.
5. Search only the selected authorized channels. Treat discovery-index records as leads until the full source is retrieved and verified.
6. Apply `safety-and-recovery.md`; acquire the browser lock and require the user to perform password, MFA, CAPTCHA, or consent steps.
7. Download only material within the user's authorized access and configured limits. Stop on authentication, permission, CAPTCHA, or rate-limit signals.
8. Preserve source provenance: title, author, date, publisher or venue, stable identifier, retrieval location, local path, and verification status.
9. Separate `verified`, `rejected`, and `unresolved` sources. Do not cite an unresolved source as verified fact.
10. Build a source registry and citation ledger before drafting.

## Planning

1. Extract claims and constraints from the brief and rubric.
2. Build an evidence matrix mapping each planned claim to one or more eligible sources.
3. Flag unsupported claims, source conflicts, and evidence gaps.
4. Write the content plan as Markdown in `04_content_plan/`.
5. Include thesis, section purpose, approximate word allocation, paragraph logic, evidence assignments, counterarguments, and citation targets.
6. Obtain user approval of the content plan before drafting. Combine minor questions into this checkpoint instead of adding section-by-section approvals.

## Drafting and review

1. Draft the complete requested artifact unless the user asks for staged output.
2. Use only sources marked citation-eligible in the source registry.
3. Keep every in-text citation traceable to the citation ledger and bibliography record.
4. Do not fabricate quotations, page numbers, publication facts, DOIs, URLs, or access dates.
5. Run independent checks for:
   - assignment and rubric compliance;
   - claim-to-source support;
   - citation and reference-list consistency;
   - source eligibility;
   - structure, argument, coherence, and word count;
   - accidental plagiarism or over-close paraphrase;
   - unsupported certainty and unresolved contradictions.
6. Revise failed checks before final delivery. Preserve the review report in `06_review/`.
7. Save the approved content in `07_final_internal/`. Ask for Word, PDF, or both, then create `<task-name>_result/`, render and validate the selected files, and write `task_summary.md` with decisions, sources used, unresolved issues, and output paths.
8. Run `scan_sensitive_artifacts.py` before delivery and finish the run state only after all required gates pass.

## Stop conditions

Pause and ask the user when any of these conditions holds:

- the assignment identity or requested deliverable is unclear;
- required authorized access needs user interaction;
- a required source cannot be obtained or verified;
- the requested citation style is institution-specific but its guide is unavailable;
- the available evidence cannot support the required claims;
- proceeding would overwrite or delete user data.
