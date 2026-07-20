# Artifact Contracts

Artifact schema v1.2 uses UTF-8, stable IDs, UTC ISO-8601 timestamps, atomic replacement for state files, and workspace-relative paths. JSON files are machine state; Markdown files are human-readable reports. Do not place credentials, cookies, access tokens, local usernames, absolute machine paths, signed URLs, prompts, or source text in state/events. Readers should continue to accept schema v1.0 and v1.1 during migration.

## Contents

- Workspace and assignment state
- Material and synchronization inventories
- Source registry and citation ledger
- Evidence, plan, draft, review, and final artifacts
- Integrity rules

## Workspace state

`workspace_config.json`:

```json
{
  "schema_version": "1.2",
  "workspace_mode": "single_task|course",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "workspace_language": "en",
  "artifact_language": "English",
  "default_citation_style": "apa-7"
}
```

In `single_task` mode, `workspace_config.json` stays at the selected container root. Each task lives in a sanitized child directory containing `task_config.json`; do not duplicate workspace configuration into every task.

`assignment_config.json`:

```json
{
  "schema_version": "1.2",
  "assignment_id": "assignment-...",
  "course_id": null,
  "title": "",
  "source_scope": "user_materials_only|course_only|external_only|mixed",
  "external_access": "institutional_library|public_sources|both|none",
  "citation_style": "apa-7",
  "language": "en",
  "word_target": null,
  "due_at": null,
  "plan_approved": false,
  "slide_citation_policy": "prohibited|allowed_by_user_confirmation",
  "slide_permission_scope": null,
  "slide_permission_basis": null,
  "delivery_formats": []
}
```

For a single-task workspace, store equivalent task-level fields in `task_config.json`; use `task_id` and `task_name`, omit `course_id`, and keep `plan_approved` false until the user approves the saved content plan. Preserve field-level intake provenance and blocking decisions in a brief extraction artifact or configuration extension.

For course mode, `course_catalog.json` lists courses and local paths; each `course_manifest.json` records course identity, LMS path, active/archive state, and last sync. Never identify a course by display name alone when a stable LMS ID is available.

## Material and sync inventories

Remote inventory must represent every observed LMS activity, including native activities and excluded video links. Remote and local inventory rows use compatible identity fields:

```json
{
  "course_id": "course-001",
  "remote_item_id": "stable-id-or-null",
  "name": "original filename or item title",
  "material_type": "journal_article|book_chapter|lecture_slides|assignment_brief|other",
  "dashboard_path": "Course > Module > Item",
  "clean_url": null,
  "module": null,
  "availability": "available|locked|hidden|unknown",
  "record_role": "downloadable_file|metadata_only|excluded_video",
  "download_eligible": true,
  "modified_at": null,
  "size_bytes": null,
  "local_path": null,
  "sha256": null,
  "verification_status": "pending|verified|failed"
}
```

Do not store a historical `download_status: downloaded` in the remote inventory. Remote observation, local availability, and current-run action are separate states.

Sync comparison status is one of `verified_match`, `unchanged`, `new`, `updated`, `renamed`, `local_missing`, `local_corrupt`, `locked`, `download_failed`, `remote_removed`, `excluded_video`, `metadata_only`, `unresolved_identity`, `content_change_unknown`, `course_added`, or `course_archived`. Every sync result also records:

```json
{
  "comparison_status": "unchanged",
  "operation_action": "skipped_existing",
  "download_attempted": false
}
```

Valid actions include `downloaded_new`, `downloaded_update`, `redownloaded_missing`, `redownloaded_corrupt`, `skipped_existing`, `metadata_updated`, `retained_local`, `attempted_failed`, and `none`. Produce both `missing_materials.md` and `missing_materials.json`; the Markdown table must include material name, full dashboard path, type, status, reason, last checked, remote location, and suggested action.

`sync_state.json` stores compact result rows and references the authoritative remote/local inventory paths. It must not embed duplicate full `remote` and `local` records. A row may add `material_type`, `local_path`, and `local_integrity_status` for diagnosis.

## Run and resume state

Each substantial task, synchronization, or assignment run may keep `run_state.json`, compact `resume_state.json`, and sanitized `events.jsonl` at its operation root. `run_state.json` records `run_id`, mode, operation, overall status, current stage, last successful checkpoint, timestamps, and stage records with status, attempts, workspace-relative inputs/outputs, stable error code, short message, and recovery hint. `resume_state.json` contains only the fields required to resume plus blockers and recent key artifacts.

Events are append-only operational metadata. Never put prompts, course/source text, bibliographic content, credentials, signed URLs, authorization data, or absolute paths in an event. Missing or partial state is diagnosed; it is never proof a stage succeeded.

## Source registry

`source_registry.json` contains CSL-compatible work records plus workflow fields:

```json
{
  "schema_version": "1.2",
  "sources": [{
    "id": "src-001",
    "type": "article-journal",
    "title": "",
    "author": [],
    "issued": null,
    "DOI": null,
    "URL": null,
    "origin": "course_lms|institutional_library|public_web|user_upload",
    "original_material_type": "journal_article",
    "source_role": "evidence|context|context_only|task_constraint|excluded",
    "citation_eligibility": "allowed|requires_verification|conditional|prohibited|not_bibliographic_evidence",
    "slide_permission_status": null,
    "verification_status": "pending|verified|rejected",
    "local_path": null,
    "verification_notes": ""
  }]
}
```

`citation_ledger.csv` uses columns:

```text
citation_id,claim_id,source_id,locator,use_type,quote_verified,draft_locations,notes
```

`use_type` is `quotation`, `paraphrase`, `data`, `definition`, or `background`. Store normalized bibliographic export as `references.bib` or CSL JSON when useful, but the source registry remains authoritative.

## Evidence and plan

`evidence_matrix.md` or JSON must map:

```text
claim_id | proposed claim | source_id | locator | support type | counterevidence | confidence | notes
```

`content_plan.md` must include assignment interpretation, thesis/research question, section word budgets, paragraph purposes/models, mapped claim/source IDs, counterarguments, and unresolved decisions. Record approval time and any approved exceptions separately; do not overwrite the original approved plan without a change note.

## Draft, review, and final

- Drafts live under the draft folder with a version suffix or manifest entry.
- `review_report.md` separates blocking failures, substantive improvements, and optional edits; each issue references a section, paragraph, claim, or citation ID.
- `07_final_internal/` for a single task or `08_final_internal/` for a course assignment contains approved content, the final source registry snapshot, citation ledger, and validation report.
- After the user selects Word, PDF, or both, `<task-name>_result/` contains only the selected user-facing files and a concise delivery-validation record. Do not create this result directory before format confirmation.
- `task_summary.md` contains goal, course, source scope, decisions, outputs, unresolved issues, and reusable course-memory updates. It must summarize artifacts rather than copy the full conversation.

## Integrity rules

- Never mark `plan_approved`, `verified`, or a gate as passed without evidence.
- Preserve old versions when a remote source changes; record supersession.
- Missing values are `null` or explicitly unresolved, never guessed.
- All artifact paths referenced in state files must exist at final validation, except remote-only records explicitly marked unavailable.
