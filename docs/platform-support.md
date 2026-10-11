# Platform Support

| Platform | Status | Notes |
| --- | --- | --- |
| Codex | Tested | Primary target; includes a marketplace catalog, plugin manifest, and `agents/openai.yaml`. |
| Agent Skills-compatible clients | Experimental | The core `SKILL.md`, `scripts`, `references`, and `assets` layout is portable, but tool and browser behavior varies. |
| Claude Code | Not yet verified | No `.claude-plugin` manifest is included. |
| Cursor | Not yet verified | No Cursor-specific adapter is included. |
| CodeBuddy/WorkBuddy and other AI IDEs | Not yet verified | Compatibility must not be claimed without an end-to-end test. |

Platform adapters should remain thin. Safety rules, artifact schemas, and academic workflow behavior belong in the common skill rather than being duplicated in each adapter.

A platform is considered supported only after tests confirm skill discovery, conditional reference loading, script execution, user checkpoints, authenticated-browser boundaries, workspace writes, recovery, and final delivery.

## Browser routes

| Route | Requirement | Validation boundary |
| --- | --- | --- |
| Codex built-in browser | Exposed Browser Use interface and site/download access | Verify page observation, download completion and a locally readable file |
| CDP | Authorized per-tab CDP capability or permitted local endpoint plus existing Playwright | Verify the selected origin/tab; Chromium attachment and API support vary |
| User computer control | Enabled host Computer Use tool/plugin and selected native window | Verify current window state and file association; unavailable when host policy disables it |

These routes are documented integrations, not bundled browser or desktop drivers. A working built-in browser does not prove native control or direct CDP attachment is enabled. Follow [browser access](../plugins/vibe-academic-writing/skills/develop-academic-paper/references/browser-access.md); do not claim an institution-specific sync works until tested with authorized access.
