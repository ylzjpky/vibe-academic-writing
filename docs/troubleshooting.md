# Troubleshooting

## Skill is not discovered

Confirm that the installed directory contains `SKILL.md` directly and that its folder name is compatible with the client. Refresh the client's skill list after installation.

## Workspace preflight fails

Use a writable local directory. If the directory is cloud-synchronized, select local storage or explicitly acknowledge the sync risk. Do not weaken the preflight check globally.

## Login, CAPTCHA, 401, 403, or 429

Do not loop retries. Let the user complete interactive authentication. For access denial or rate limiting, record the failure, release the browser lock when safe, and follow the provider's policy or wait for the user to resolve access.

## Wrong course page detected

Return to the page that visibly lists the user's courses, rerun the course-page validation gate, and ask the user to confirm detected course names and count before creating or updating the catalog.

## A course file is missing

Compare the remote inventory, verified local inventory, and sync state. Record the remote label and breadcrumb path in `missing_materials.md`. Do not claim a download succeeded without a local artifact and verification result.

## The browser opens pages but synchronization fails

Follow [browser access](../plugins/vibe-academic-writing/skills/develop-academic-paper/references/browser-access.md). Check whether the selected tool exposes download events and a locally readable file path; page access alone is insufficient. For a native dialog use the confirmed directory snapshot method. Use `download_map.json` with `verify_downloads.py --download-map` when the browser renamed a file or different modules contain the same filename. Keep remote identities in the resulting local inventory.

For missing CDP or native UI capability, use an available built-in browser or another allowed route and revalidate the target/session. Do not switch routes to retry authentication, access denial, CAPTCHA, or rate-limit failures. A policy-disabled route remains disabled; manual download is the fallback when no allowed route can receive files.

If a role-based click finds no matches, inspect the current DOM snapshot before retrying. Accessibility and DOM roles can differ for expandable controls such as `<summary>`; use the observed text or attributes for the same control and verify that the section expanded.

## Validation fails

Run `diagnose_run.py`, inspect the stable error code and affected artifact, fix the earliest failed dependency, then rerun only stale downstream stages. Avoid restarting a successful authenticated download stage when file hashes still verify.

## Sensitive-data scanner reports a finding

Stop sharing and publishing. Remove the value at its source, rotate or revoke it when appropriate, and rerun the scan. Do not copy the detected secret into chat, issues, logs, or diagnostic reports.
