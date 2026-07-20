# Architecture

Vibe Academic Writing separates a marketplace-installable plugin wrapper, a compact runtime skill, and repository documentation and validation.

## Runtime layers

1. `.agents/plugins/marketplace.json` exposes the repository as a Codex marketplace.
2. `plugins/vibe-academic-writing/.codex-plugin/plugin.json` identifies the installable plugin and its Skill path.
3. `SKILL.md` provides routing rules, invariants, checkpoints, and the core workflow.
4. `references/` contains conditionally loaded procedures and policies.
5. `scripts/` performs deterministic state, validation, synchronization, and safety operations without consuming model context for implementation details.
6. `assets/workspace-templates/` defines reusable initial workspace records.
7. `agents/openai.yaml` contains OpenAI-facing display metadata and a default invocation prompt.

The main agent owns user decisions, authenticated browser control, conflict resolution, and final synthesis. Subagents may process bounded local artifacts, but only one agent may control an authenticated browser at a time.

## Execution routes

- Single task: intake, task directory, source scope, research, evidence matrix, approved plan, draft, review, export.
- Course initialization: validate the course-list page, confirm catalog, create course workspaces, synchronize materials, verify inventory.
- Course resynchronization: scan remote metadata, compare with prior remote and verified local inventory, retrieve only changed or newly available material.
- Course assignment: select course, resolve course/external/mixed source scope, check snapshot currency, then reuse the single-task research and writing pipeline.

Run state is persisted as compact artifacts so a later conversation can resume from verified files rather than replaying full chat history.
