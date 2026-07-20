# Long-term course mode

Use this workflow to create or resume a workspace that stores course materials and course assignments across conversations. Treat synchronization and assignment execution as separate operations.

## First-use routing

1. Inspect the selected root directory.
2. If no valid `workspace_config.json` exists, ask whether the user wants `single_task` or `course` mode.
3. Continue here only after the user selects `course`.
4. Run workspace preflight. Collect the institution name, dashboard entry point, active-versus-archived course scope, preferred language, default citation style, and desired non-video material scope.
5. Do not collect or store passwords, MFA secrets, recovery codes, or session cookies.
6. Set `workspace_mode` to `course` and assign a stable workspace identifier.

## Workspace structure

Create only missing paths. Sanitize filesystem names while preserving the displayed course name in metadata.

```text
course-workspace/
  workspace_config.json
  course_catalog.json
  sync_overview.md
  courses/
    <course-slug>/
      course_manifest.json
      01_course_materials/
      02_course_library/
      03_assignments/
      04_course_memory/
        course_memory.md
        task_index.csv
      05_sync/
      90_missing_materials/
```

Do not place files from different courses in the same course directory. Use stable course IDs to disambiguate identical course names.

## First synchronization

1. Ask the user to sign in and navigate to the institution's course-list page.
2. Acquire `browser.lock`, then apply the gate in `course-page-validation.md`. Do not enumerate or create course directories until the gate passes.
3. Read the visible in-scope courses and construct a proposed catalog with course names and stable identifiers when available.
4. Show the detected course count and names. Require user confirmation before creating or renaming course directories.
5. Create the confirmed catalog and course directories.
6. Run the first-sync workflow in `course-sync.md` one course at a time.
7. Download eligible non-video materials, preserve the LMS hierarchy, verify local files, and generate missing-material reports.
8. Write the final counts and unresolved failures to `sync_overview.md`.

## Resume behavior

At the start of a later conversation:

1. Read `workspace_config.json`, `course_catalog.json`, and compact `resume_state.json` when present.
2. Read full run state only for a blocker; otherwise read only the selected course's manifest, memory, task index, and relevant task summaries.
3. Inspect the catalog and course directories once on entry; do not continuously monitor them or scan the LMS in the background.
4. Ask the user to select one course when more than one exists. Then offer:
   - synchronize or resynchronize only;
   - start a course assignment only;
   - synchronize, then start an assignment;
   - continue an existing assignment;
   - inspect sync or missing-material status;
   - return to course selection.
5. Do not scan all historical drafts or raw conversations by default.
6. Use files as the durable state. Treat conversational memory as supplemental and non-authoritative.

## Assignment routing

When the user requests coursework rather than synchronization:

1. Route to `course-assignment-mode.md`.
2. Require a course selection or confirmation.
3. Do not force a sync if the existing manifest is current enough for the task. State the last sync time and let the user choose; recommend a lightweight resync only when stale or missing material can affect the task.
4. Store the assignment under the selected course's `03_assignments/` directory.
5. Update `task_index.csv` and `course_memory.md` after final delivery.

## Catalog changes

Require user confirmation before applying detected course additions, renames, archive-state changes, or course-ID conflicts. Never delete a local course directory merely because a course is absent from the current dashboard view. Mark it `not_observed`, `archived`, or `remote_removed` as supported by the evidence.

## Safety invariants

- Keep credentials out of all files and prompts intended for persistence.
- Operate only within the user's authorized accounts and materials.
- Never use concurrent browser-controlling agents against the same LMS session.
- Never overwrite changed local files during sync without version preservation.
- Never treat successful clicking as proof of a valid download; verify the local file.
- Treat lecture slides as non-citable by default. Apply a recorded task/course permission only through the slide policy in `course-assignment-mode.md`.
