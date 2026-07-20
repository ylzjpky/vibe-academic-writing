# Platform Support

| Platform | Status | Notes |
| --- | --- | --- |
| Codex | Tested | Primary target; includes `agents/openai.yaml`. |
| Agent Skills-compatible clients | Experimental | The core `SKILL.md`, `scripts`, `references`, and `assets` layout is portable, but tool and browser behavior varies. |
| Claude Code | Not yet verified | No `.claude-plugin` manifest is included. |
| Cursor | Not yet verified | No Cursor-specific adapter is included. |
| CodeBuddy/WorkBuddy and other AI IDEs | Not yet verified | Compatibility must not be claimed without an end-to-end test. |

Platform adapters should remain thin. Safety rules, artifact schemas, and academic workflow behavior belong in the common skill rather than being duplicated in each adapter.

A platform is considered supported only after tests confirm skill discovery, conditional reference loading, script execution, user checkpoints, authenticated-browser boundaries, workspace writes, recovery, and final delivery.
