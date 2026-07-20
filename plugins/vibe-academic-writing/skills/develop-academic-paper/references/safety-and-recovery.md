# Safety and recovery

Load this reference before authenticated browsing, institutional retrieval, course downloads, or recovery from a failed stage.

## Storage preflight

Run `scripts/preflight_workspace.py <workspace>` before creating or downloading into a workspace. Treat exit code `2` as blocked. If OneDrive, Dropbox, iCloud, Google Drive, Box, or another synchronized location is detected, explain that licensed/private files may be uploaded automatically. Continue only after the user chooses a non-synced directory or explicitly confirms that storage is permitted; record confirmation with `--acknowledge-cloud-sync`.

Default download limits are 500 files per run, 512 MiB per file, and 2 GiB total. Ask before raising a limit and record the approved value in the run state. These are safety caps, not claims about institutional policy.

Share only the result directory by default. Do not send licensed course/e-library files, source text, inventories, or workspace state to external services, plugins, connectors, or unrelated agents unless the user authorizes that destination and the license permits it. Do not create retention copies outside the workspace.

Default retention is user-managed: never delete course/source files automatically. If the user asks for cleanup, inventory exact targets, distinguish results from licensed/private source material, and use a recoverable deletion method when available.

## Authentication and account protection

- The user performs password, passkey, MFA, recovery, consent, and CAPTCHA steps in the site UI.
- Never place credentials, cookies, authorization headers, signed URLs, proxy tokens, or local usernames in prompts, handoffs, artifacts, or events.
- Use one browser owner and one navigation/download at a time. Acquire `browser.lock` with `browser_lock.py`, renew it during a long active run, and release it when pausing or finishing.
- Operate at a normal interactive pace. Do not parallelize pages or downloads, enumerate hidden endpoints, rotate identities, imitate another client, or use direct endpoints not exposed by the normal interface.
- Pause 2–5 seconds between automated page transitions unless the site itself controls timing. Site limits override this default.
- Stop on CAPTCHA, unusual-login warnings, consent changes, session expiry, `401`, `403`, or `429`. Do not automatically retry these conditions.
- Retry only transient connection or `5xx` failures, at most twice, with increasing delays such as 5 and 15 seconds. If the same operation still fails, record it and continue only where independent work is safe.
- A generic skill cannot guarantee that an institution will not flag automation. When terms or permitted behavior are unclear, stop and ask the user to use a manual export.

## Download handling

Snapshot the download directory before each action and move only newly created files that match the intended item. Verify file name/identity, non-zero size, expected signature, and hash. A browser click or success banner is not sufficient.

Never execute downloaded scripts or macros. Treat `.docm`, `.xlsm`, `.pptm`, and related macro-enabled Office files as `unsafe_macro`. Treat archives as `archive_requires_review`; do not extract them automatically. Do not open active content merely to inspect it. Use platform malware scanning when available, but never describe a signature/hash check as a malware scan.

Run `verify_downloads.py` with the active limits. Quarantine or leave in the incoming area any file that fails verification; do not make it available to drafting or subagents.

## Sensitive artifact control

Durable URLs must be cleaned with `redact_url`; prefer DOI, catalog permalink, or stable resolver URLs. Run `scan_sensitive_artifacts.py` after authenticated retrieval and before final delivery. It scans JSON, JSONL, Markdown, CSV/TSV, logs, YAML, text, and BibTeX for credential assignments, bearer/basic headers, JWT-like values, URL userinfo, and signed queries. It reports the location and finding type without copying the secret value.

If a finding appears, stop persistence/sharing, remove or replace the secret at its source, invalidate it when appropriate, rerun the scan, and record `SENSITIVE_DATA_DETECTED`. Do not paste the detected value into chat or the diagnostic report.

## State, error codes, and recovery

Use `manage_run_state.py` at operation root:

```text
manage_run_state.py start <root> --mode <mode> --operation <name>
manage_run_state.py stage <root> --stage <stage> --status running
manage_run_state.py stage <root> --stage <stage> --status succeeded --output <relative-path>
manage_run_state.py stage <root> --stage <stage> --status blocked --error-code <code> --recovery-hint <safe-text>
manage_run_state.py finish <root> --status succeeded
```

The script atomically writes `run_state.json`, derives compact `resume_state.json`, and appends sanitized `events.jsonl`. Events contain no prompts, source text, credentials, or absolute paths.

Use stable codes: `AUTH_REQUIRED`, `SESSION_EXPIRED`, `PAGE_GATE_FAILED`, `RATE_LIMITED`, `PERMISSION_DENIED`, `CLOUD_SYNC_WORKSPACE`, `DOWNLOAD_LIMIT_EXCEEDED`, `DOWNLOAD_MISMATCH`, `UNSAFE_FILE`, `SENSITIVE_DATA_DETECTED`, `SOURCE_UNVERIFIED`, `PLAN_STALE`, `VALIDATION_FAILED`, `RENDER_FAILED`, `TOOL_UNAVAILABLE`, `TRANSIENT_NETWORK_ERROR`, or `UNKNOWN_FAILURE`.

On failure:

1. Mark the stage failed or blocked and give a non-secret recovery hint.
2. Release browser ownership if no protected action remains in progress.
3. Run `diagnose_run.py <root>` to summarize state and validator evidence.
4. Fix the blocker and rerun that stage only.
5. Rerun downstream gates whose inputs changed. If the brief changes, invalidate plan/draft/review/delivery; if sources change, invalidate evidence/citations/review/delivery; if only rendering changes, rerun render and delivery validation.

Do not delete earlier verified versions during recovery. Atomic artifact writes protect individual state files, but source and draft version history still needs explicit preservation.
