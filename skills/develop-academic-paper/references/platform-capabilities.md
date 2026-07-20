# Platform capability adapter

Read this only when running outside Codex or when a required tool is unavailable.

The portable core is `SKILL.md`, relative references, local artifacts, and standard-library Python scripts. `agents/openai.yaml` is Codex-specific metadata and may be ignored elsewhere.

Before starting, determine whether the current surface provides:

| Capability | Required for | Safe fallback |
| --- | --- | --- |
| Workspace-scoped file writes | Every mode | Ask the user to select/grant one project folder |
| Local Python execution | Deterministic setup, state, sync, and validation | Run equivalent steps manually and preserve the same artifacts; do not claim validators ran |
| Authenticated browser/computer control | LMS/e-library navigation | Ask for user-exported files and inventories |
| Subagents | Parallel retrieval/independent review | Execute role contracts sequentially with a distinct review pass |
| Word/PDF renderer | Final delivery | Produce the supported format or give the editable source and disclose the limitation |
| Approval/sandbox controls | Authenticated or external actions | Ask the user before material actions and keep all writes inside the workspace |

Claude Code and CodeBuddy can consume the Agent Skills-style directory, but their frontmatter, tool names, hooks, subagent definitions, install paths, and browser integrations differ. Keep platform-specific permissions in an adapter or product configuration rather than the portable Skill core. Do not add `context: fork`, `allowed-tools`, or hooks to the shared frontmatter unless building a platform-specific package.

WorkBuddy compatibility must be established by a real import/execution test. If its client cannot load this directory, use the workflow as a project instruction set and keep the deterministic artifacts/scripts local. Never infer authenticated-browser or file-system capability from the presence of a generic “Skill” feature.
