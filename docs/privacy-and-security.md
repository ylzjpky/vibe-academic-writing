# Privacy and Security

## Authentication

Users perform passwords, passkeys, MFA, CAPTCHA, recovery, and consent steps directly in the provider's interface. These values must never be requested in chat, written to files, placed in agent handoffs, or committed to a repository.

Authenticated navigation is limited to resources the user is authorized to access. The workflow stops for access denial, anti-bot signals, ambiguous permissions, or institutional restrictions instead of retrying aggressively or attempting a bypass.

## Stored data

Workspaces may contain assignment briefs, downloaded course material, source records, inventories, plans, drafts, and final deliverables. They should remain in a user-confirmed local workspace. Cloud-synchronized directories require explicit acknowledgement because they may upload material to a third party.

State files must use clean URLs and workspace-relative paths. They must not contain credentials, cookies, authorization headers, signed URLs, local usernames, full prompts, or unnecessary source text.

## Repository safety

Do not use a real course workspace as a Git checkout. This repository ignores common runtime artifacts, but ignore rules are not a security boundary. Before any contribution or release:

1. inspect staged filenames;
2. run the sensitive-artifact scanner on the proposed content;
3. review the Git diff;
4. confirm all examples and fixtures are synthetic;
5. verify that no large binary course files are present.

## Academic and legal responsibility

Course synchronization does not transfer ownership or redistribution rights. Users remain responsible for institutional acceptable-use rules, copyright, privacy, assignment collaboration rules, disclosure requirements, and academic integrity. Generated text should be reviewed and used only where permitted.
