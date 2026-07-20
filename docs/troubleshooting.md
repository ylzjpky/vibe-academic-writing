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

## Validation fails

Run `diagnose_run.py`, inspect the stable error code and affected artifact, fix the earliest failed dependency, then rerun only stale downstream stages. Avoid restarting a successful authenticated download stage when file hashes still verify.

## Sensitive-data scanner reports a finding

Stop sharing and publishing. Remove the value at its source, rotate or revoke it when appropriate, and rerun the scan. Do not copy the detected secret into chat, issues, logs, or diagnostic reports.
