# Institutional E-Library Workflow

Use this workflow only for resources the user is authorized to access. Apply `safety-and-recovery.md`, including browser locking, stop/retry rules, storage preflight, and download caps. Respect the institution's terms, copyright controls, download limits, and robots or rate limits.

## Authentication boundary

- Ask the user to enter passwords, MFA codes, CAPTCHA responses, or other secrets directly in the institution's interface.
- Never request that credentials be pasted into chat, write credentials to files, log them, or include them in agent handoffs.
- Reuse an authorized browser session only while it remains available. If authentication expires, pause for the user.
- Do not bypass a paywall, access control, DRM, download restriction, geographic restriction, or concurrency limit.
- Do not share licensed files outside the user's authorized workspace.

## Retrieval procedure

1. Record the research question, source scope, external-access selection, course, date range, preferences, and inclusion criteria.
2. Ask the user to choose the school e-library, public scholarly sources, or both when external retrieval is needed and no choice is stored. Treat Google Scholar and similar indexes as discovery tools rather than verified full-text sources.
3. Open the item record and verify title, authors, publication, year, identifiers, and full-text availability.
4. Download only when the interface permits it and the download is relevant to the task. Avoid bulk harvesting.
5. Save task-specific documents under the assignment source folder; save reusable course holdings under the course library folder.
6. Verify that each downloaded file opens, is complete, and matches the item record.
7. Register provenance and citation metadata; record inaccessible items without fabricating content.

## Browser control

Only the designated Browser/LMS Navigator agent may control the browser during a run. Other agents may inspect saved files and inventories. Keep browser navigation sequential so two agents cannot alter the same session, course, tab, or download state.

## Retrieval record

For each result record:

```json
{
  "source_id": "src-...",
  "origin": "institutional_library",
  "database": "database name",
  "record_url": "stable item or resolver URL",
  "accessed_at": "ISO-8601 timestamp",
  "access_status": "downloaded|metadata_only|login_required|permission_denied|not_available",
  "local_path": null,
  "license_note": null
}
```

Do not store session cookies, authorization headers, proxy URLs containing tokens, or signed download URLs as durable provenance. Prefer DOI, permalink, catalogue record, or clean resolver URL.

## Failure handling

- `login_required` or MFA: pause and ask the user to complete authentication.
- `permission_denied` or unavailable full text: preserve verified metadata and the dashboard/database path; report it as unresolved.
- Download failure: retry only a transient connection/`5xx` failure under the bounded retry policy; never retry authentication, permission, CAPTCHA, or `429` automatically. Record the failure and continue only with independent sources.
- Metadata conflict: retain both candidate values, link evidence, and send the item to source verification.
