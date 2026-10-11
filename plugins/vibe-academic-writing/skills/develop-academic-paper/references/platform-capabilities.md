# Platform capability adapter

Read this only when running outside Codex or when a required tool is unavailable.

The portable core is `SKILL.md`, relative references, local artifacts, and standard-library Python scripts. `agents/openai.yaml` is Codex-specific metadata and may be ignored elsewhere.

Before starting, determine whether the current surface provides:

| Capability | Required for | Safe fallback |
| --- | --- | --- |
| Workspace-scoped file writes | Every mode | Ask the user to select/grant one project folder |
| Local Python execution | Deterministic setup, state, sync, and validation | Run equivalent steps manually and preserve the same artifacts; do not claim validators ran |
| Codex built-in browser | New browser sessions, public research, LMS/e-library navigation | Reuse an available authorized CDP browser or computer-use surface |
| Authorized CDP browser/capability | Existing Chromium sessions and frame/control diagnosis | Use the built-in browser or enabled computer-use surface |
| Enabled computer control | Existing user browser windows and native download dialogs | Use an available browser interface; otherwise request manual export |
| Download event/local file access | Course and literature downloads | Snapshot the confirmed download directory or request manual download |
| Subagents | Parallel retrieval/independent review | Execute role contracts sequentially with a distinct review pass |
| Word/PDF renderer | Final delivery | Produce the supported format or give the editable source and disclose the limitation |
| Approval/sandbox controls | Authenticated or external actions | Ask the user before material actions and keep all writes inside the workspace |

Claude Code and CodeBuddy can consume the Agent Skills-style directory, but their frontmatter, tool names, hooks, subagent definitions, install paths, and browser integrations differ. Keep platform-specific permissions in an adapter or product configuration rather than the portable Skill core. Do not add `context: fork`, `allowed-tools`, or hooks to the shared frontmatter unless building a platform-specific package.

WorkBuddy compatibility must be established by a real import/execution test. If its client cannot load this directory, use the workflow as a project instruction set and keep the deterministic artifacts/scripts local. Never infer authenticated-browser or file-system capability from the presence of a generic “Skill” feature.

For every browser operation, follow [browser-access.md](browser-access.md). Discover actual tools and per-tab capabilities; a plugin installation, an advertised CDP capability, or an empty app inventory does not establish permission, login, or working download access. The portable Python scripts do not launch a browser or enable host permissions. Browser/computer features may be absent or disabled in CLI, IDE, remote, or managed environments.
