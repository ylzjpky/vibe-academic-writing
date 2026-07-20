# Course material synchronization

Use this workflow after the course-list page gate, catalog confirmation, and workspace preflight. Support `first_sync`, lightweight `resync`, and user-requested `deep_resync`. Control one LMS browser session sequentially under `browser.lock`; parallelize only local, read-only verification when safe. Apply the limits and stop/retry rules in `safety-and-recovery.md`.

## Contents

- Scope and remote inventory
- First synchronization
- Resynchronization and reconciliation
- Missing-material reporting
- Material policy and completion

## Scope

Synchronize user-authorized, downloadable non-video course materials, including PDF, DOCX, PPT, PPTX, XLSX, text files, images, archives, and other explicitly requested document formats. Do not download video. Record video entries as `excluded_video` with their dashboard path. Macro-enabled Office files and archives may be retained only for manual review; never execute macros or automatically extract archives.

For LMS-native pages, store metadata and a stable location by default. Export the page only when the LMS provides an authorized export or print action and the user wants local copies.

## Remote inventory

Before downloading, enumerate the in-scope course hierarchy and create a remote inventory. Preserve the LMS organization: term, module, week, topic, unit, folder, or section. When the LMS is flat, group by material type without inventing academic categories. Represent every observed activity, not only downloadable files. Use `record_role: downloadable_file`, `metadata_only`, or `excluded_video` so manifest counts reconcile with the machine inventory.

Record at least:

```json
{
  "course_id": "course-001",
  "remote_item_id": "lms-id-if-available",
  "name": "Week 2 reading.pdf",
  "material_type": "pdf",
  "dashboard_path": "Courses > Course Name > Modules > Week 2",
  "clean_url": "redacted stable URL",
  "module_path": "Modules > Week 2",
  "availability": "available",
  "record_role": "downloadable_file",
  "download_eligible": true,
  "modified_at": null,
  "size_bytes": null
}
```

Redact secret URL parameters. Retain enough location information for the user to find an item manually.

## First sync

For each confirmed course, sequentially:

1. Open the course and verify that its displayed name or stable ID matches the target manifest.
2. Enumerate all in-scope material areas and write the remote inventory before bulk downloading.
3. Exclude videos and record them without downloading.
4. Download each eligible non-video item to a controlled incoming directory when possible.
5. If downloads must enter the browser's default download directory, snapshot its inventory first and move only files created by the current action.
6. Verify each file by existence, nonzero size, expected type or signature, readable container, and association with the intended remote item.
7. Move verified files into `01_course_materials/` while reproducing the LMS hierarchy.
8. Keep original names when safe. Resolve collisions with stable IDs or deterministic suffixes; record the mapping.
9. Generate the local inventory with paths, sizes, modification times, hashes when practical, and verification status.
10. Compare remote eligible items with verified local files.
11. Write the sync state, history, summary, and missing-material report.

Create/update the operation `run_state.json` at each numbered checkpoint. Stop before downloads when the configured file-count or byte cap would be exceeded.

## Lightweight resync

Default to a page-and-metadata scan. Read the previous remote inventory and current local inventory, scan the course hierarchy again, and write a fresh complete remote inventory. Do not open, extract, OCR, hash, or redownload unchanged remote files. Compare deterministically before any download and match in this order:

1. stable remote item ID;
2. canonical URL without secret or volatile parameters;
3. dashboard path plus original name;
4. name plus remote size;
5. name plus module path;
6. verified local hash for previously downloaded versions.

Assign one status per item:

- `unchanged`: verified local match; skip download;
- `new`: not present locally; download;
- `updated`: remote metadata or content differs; download a new version and preserve the old version;
- `renamed`: stable identity matches but display name changed; update metadata and avoid duplicate content;
- `local_missing`: manifest says downloaded but file is absent; redownload;
- `local_corrupt`: local validation fails; preserve for diagnosis and redownload;
- `locked`: not yet available; do not attempt bypass;
- `download_failed`: authorized download attempt failed;
- `remote_removed`: previously observed but absent remotely; retain local file and mark status;
- `course_added`: new confirmed course; initialize and first-sync it;
- `course_archived`: retain local files and update catalog after confirmation.
- `metadata_only`: retain the LMS-native activity and stable location without treating it as a missing file;
- `unresolved_identity`: report a visible but empty, ambiguous, or incomplete native activity for user follow-up;
- `content_change_unknown`: the LMS exposes insufficient metadata to prove that content stayed unchanged.
- `unsafe_file`: macro-enabled or otherwise active content requires user review and is excluded from processing;
- `review_required`: an archive or unsupported container is retained without extraction.

Never redownload `unchanged` items. Never delete or overwrite prior versions. Store new versions deterministically and update the manifest's current-version pointer.

When stable ID, name, size, and remote modification metadata are unchanged, classify a verified local match as `unchanged` and `operation_action: skipped_existing`. Open or download only `new`, `updated`, ambiguous, locally missing, or locally corrupt items. If the LMS can replace bytes without exposing any changing signal, use `content_change_unknown`; do not overclaim. Offer `deep_resync` when the user wants stronger verification.

For every result, separate the final comparison from the action taken:

```json
{
  "comparison_status": "unchanged",
  "operation_action": "skipped_existing",
  "download_attempted": false
}
```

For a first download, use `operation_action: downloaded_new` with `comparison_status: verified_match`. For an updated file, use `downloaded_update`; for a failed attempt, use `attempted_failed`. Record operation actions explicitly rather than inferring them after the file is already present.

## Reconciliation

For each course, reconcile counts with this invariant:

```text
remote_eligible = local_verified + confirmed_missing_or_locked + download_failed
```

Count excluded videos separately. Do not claim complete synchronization when the invariant fails or when unvisited pages, pagination, or lazy-loaded sections remain.

Compare both names and identities. A matching count alone is insufficient.

## Missing-material report

Create or update both files:

```text
90_missing_materials/
  missing_materials.md
  missing_materials.json
```

Include every unavailable, locked, permission-denied, failed, corrupt, unsupported, or manually required item. The Markdown report must include at least:

| Name | Dashboard path | Type | Status | Reason | Last checked | Remote location | Suggested action |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use these status values where applicable: `locked`, `hidden`, `not_released`, `permission_denied`, `authentication_required`, `download_failed`, `local_corrupt`, `unsafe_file`, `review_required`, `unsupported`, `manual_download_required`, `unresolved_identity`.

The `Name` and `Dashboard path` columns are mandatory. Provide a safe, redacted remote location when available. Keep resolved history in the machine-readable report; remove an item from the active Markdown table only after local verification succeeds or the user confirms it is intentionally excluded.

## Material policy

Tag synchronized slides at ingestion, regardless of file extension:

```json
{
  "material_type": "lecture_slides",
  "source_role": "context_only",
  "citation_eligibility": "prohibited"
}
```

Detect exported slide PDFs from provenance, remote labels, file metadata, or layout. Preserve this tag across renames and conversions. Synchronization establishes local availability; it does not establish academic citation eligibility for any material.

## Completion report

Report per course:

- remote observed count;
- remote eligible non-video count;
- verified local count;
- unchanged, new, updated, locked, failed, and excluded-video counts;
- missing-report path;
- sync timestamp and completeness state;
- unresolved discrepancies and required user actions.

Mark the operation `complete` only when all in-scope pages were inventoried and every eligible item is either locally verified or explicitly represented in the missing-material report. Persist only workspace-relative paths and UTC timestamps.
